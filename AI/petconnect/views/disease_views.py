from flask import Flask, request, jsonify
import os
import cv2
from skimage.feature import hog
import pickle

app = Flask(__name__)

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# disease_model.pkl의 상대 경로 계산
disease_model_path = os.path.join(current_dir, '..', '..', 'disease', 'SVM-Classifier', 'disease.pkl')

# SVM 모델 로드
with open(disease_model_path, 'rb') as model_file:
    svm_model = pickle.load(model_file)

# 예측 가능한 질병 카테고리
categories = ['atopy', 'hotspots', 'hair_loss', 'normal']

@app.route('/disease', methods=['POST'])
def analyze_disease():
    if 'file' not in request.files:
        return jsonify({'error': '파일 부분이 없습니다'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다'})

    if file:
        # 업로드된 이미지를 임시 위치에 저장
        image_path = os.path.join('uploads', file.filename)
        file.save(image_path)

        # 이미지 로드 및 전처리
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        preprocessed_image = cv2.resize(image, (64, 64))
        hog_features = hog(preprocessed_image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1))

        # SVM 모델을 사용하여 질병 카테고리 예측
        predicted_label = svm_model.predict([hog_features])[0]
        predicted_category = categories[predicted_label]

        # 임시 이미지 파일 삭제
        os.remove(image_path)

        return jsonify({'result': predicted_category})

if __name__ == '__main__':
    app.run(debug=True)