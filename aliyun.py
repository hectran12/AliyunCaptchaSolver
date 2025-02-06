"""
    Model YOLO được train với số lượng hình ảnh ít ỏi (khoảng 30 ảnh), nên kết quả dự đoán chính xác không cao.
    Với cả toi lười nên đã chọn cách train tối ưu về mặc thời gian nên kết quả không được tốt:)))
    Project for fun, tôi không chú tâm vào chất lượng cho lắm, nhưng chắc chắn nó sài được.


    Base idea:
    1. Xử lý ảnh đầu vào: Chuyển ảnh màu sang ảnh xám.
    2. Dự đoán trên ảnh xám: Sử dụng mô hình YOLO để dự đoán trên ảnh xám.
    3. Xử lý kết quả dự đoán: Thêm thông tin màu sắc cho các object được dự đoán.
    4. Phân tích câu hỏi: Xác định điều kiện từ câu hỏi.
    5. Lọc object phù hợp: Lọc object phù hợp nhất dựa trên điều kiện từ câu hỏi.
    6. Hiển thị kết quả: Hiển thị kết quả dự đoán trên ảnh gốc.


    code by https://github.com/hectran12 (tronghoa2008)
"""


from ultralytics import YOLO
import cv2, os
import numpy as np

MODEL_PATH = 'model.pt'

class Utils:
    @staticmethod
    def convert_img_to_gray_scale(image_path, save_path=None):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Không thể đọc ảnh, kiểm tra lại đường dẫn!")
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if save_path:
            cv2.imwrite(save_path, gray_img)
        return gray_img


    @staticmethod
    def delete_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
class AliyunCSSolver:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.define_classes = ['ball', 'cone', 'cube', 'cylinder', 'polyhedron', 'sphere']
        self.size_keywords = ["smallest", "largest", "biggest", "tiny"]
        self.color_keywords = ["red", "blue", "yellow", "green", "gray"]
        self.shape_keywords = self.define_classes + ["object"]  # added "object"


        # color range to detect dominant color
        self.COLOR_RANGES = {
            "red": [(0, 100, 100), (10, 255, 255)],
            "blue": [(100, 100, 100), (140, 255, 255)],
            "yellow": [(20, 100, 100), (30, 255, 255)],
            "green": [(40, 50, 50), (90, 255, 255)],
            "gray": [(0, 0, 50), (180, 50, 200)]
        }

    def detect_dominant_color(self, image):
        if image is None or image.size == 0:
            return "unknown"
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_count = {color: 0 for color in self.COLOR_RANGES.keys()}
        for color, (lower, upper) in self.COLOR_RANGES.items():
            mask = cv2.inRange(hsv_img, np.array(lower), np.array(upper))
            color_count[color] = np.sum(mask > 0)
        dominant_color = max(color_count, key=color_count.get)
        return dominant_color if color_count[dominant_color] > 0 else "unknown"

    def process_detections(self, image_path, detections):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Cannot read image, please check the path!")
        for obj in detections:
            x1, y1, x2, y2 = map(int, obj["bbox"])
            cropped_img = img[y1:y2, x1:x2]
            obj["dominant_color"] = self.detect_dominant_color(cropped_img)
        return detections

    def prcs_question(self, question: str) -> dict:
        question = question.lower().replace('please click the ', '').replace('.', '')
        if 'sphere' in question:
            question = question.replace('sphere', 'ball')

        condition = {"size": None, "color": None, "shape": None}
        for word in question.split():
            if word in self.size_keywords:
                condition['size'] = 'smallest' if word == 'tiny' else word
            elif word in self.color_keywords:
                condition['color'] = word
            elif word in self.shape_keywords:
                condition['shape'] = word

        return condition

    def summary_info(self, results) -> list:
        summary = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = round(box.conf[0].item(), 2)
                class_id = int(box.cls[0].item())
                label_name = self.define_classes[class_id]

                summary.append({
                    'class': label_name,
                    'confidence': confidence,
                    'bbox': (x1, y1, x2, y2)
                })
        return summary

    def filter_best_match(self, detections, condition):

        if condition["shape"] == "object":
            filtered = detections  # process all objects if shape is "object"
        else:
            filtered = [obj for obj in detections if obj["class"] == condition["shape"]]

        if condition["color"]:
            filtered = [obj for obj in filtered if obj["dominant_color"] == condition["color"]]

        if condition["size"]:
            if condition["size"] == "smallest":
                filtered = sorted(filtered, key=lambda x: (x["bbox"][2] - x["bbox"][0]) * (x["bbox"][3] - x["bbox"][1]))
            elif condition["size"] in ["largest", "biggest"]:
                filtered = sorted(filtered, key=lambda x: (x["bbox"][2] - x["bbox"][0]) * (x["bbox"][3] - x["bbox"][1]), reverse=True)

        return filtered[0] if filtered else None

    def show_result(self, img_path, best_match):
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("Cannot read image, please check the path!")

        x1, y1, x2, y2 = best_match["bbox"]
        label = f"{best_match['class']} ({best_match['dominant_color']})"

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Solver result", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def solve(self, question: str, img_path: str, show_result=False):
        try:
            condition = self.prcs_question(question)
            img_gray = os.path.join(os.path.dirname(img_path), os.path.basename(img_path).split('.')[0] + "_gray.jpg")
            Utils.convert_img_to_gray_scale(img_path, img_gray)
            results = self.model(img_gray)
            summary = self.summary_info(results)
            detections = self.process_detections(img_path, summary)
            best_match = self.filter_best_match(detections, condition)
            # delete temp file
            Utils.delete_file(img_gray)
            if best_match:
                if show_result:
                    self.show_result(img_path, best_match)
                    return True
                
                x1, y1, x2, y2 = best_match["bbox"]
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2


                return x, y
            else:
                print("No object found!")
                return False

        except Exception as e:
            print("Error:", e)
            return False
