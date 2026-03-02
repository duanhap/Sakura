import random
from app.extensions import db
from app.models import Sentence, ResultUnitTest

class TestService:
    @staticmethod
    def generate_test(unit_id):
        sentences = Sentence.query.filter_by(UnitId=unit_id).all()
        if not sentences:
            return {"success": False, "message": "Không có câu nào trong bài học này để tạo bài kiểm tra."}

        # Lấy tất cả các ký tự từ tất cả các câu để làm distractor cho phần nghe
        all_chars = set()
        for s in sentences:
            for char in s.content:
                if char.strip() and char not in '.,;!?。，！？、': # Loại bỏ dấu câu
                    all_chars.add(char)
        
        all_chars = list(all_chars)

        questions = []
        # Chon ngẫu nhiên 15 câu (có thể lặp lại nếu số câu < 15, nhưng cố gắng unique nếu có thể)
        selected_sentences = random.choices(sentences, k=15) if len(sentences) < 15 else random.sample(sentences, 15)
        
        # Xáo trộn để phân loại
        random.shuffle(selected_sentences)
        
        # 5 câu nghe
        for i in range(5):
            s = selected_sentences[i]
            chars = [c for c in s.content if c.strip() and c not in '.,;!?。，！？、']
            distractors = []
            available_distractors = [c for c in all_chars if c not in chars]
            if available_distractors:
                distractors = random.sample(available_distractors, min(4, len(available_distractors)))
            
            options = chars + distractors
            random.shuffle(options)
            
            questions.append({
                "id": s.id,
                "type": "listen",
                "content": s.content,
                "pronunciation": s.pronunciation,
                "meaning": s.meaning,
                "options": options,
                "answer": chars
            })

        # 5 câu nói
        for i in range(5, 10):
            s = selected_sentences[i]
            questions.append({
                "id": s.id,
                "type": "speak",
                "content": s.content,
                "pronunciation": s.pronunciation,
                "meaning": s.meaning
            })

        # 3 câu đọc (Cho thuật ngữ, viết nghĩa)
        for i in range(10, 13):
            s = selected_sentences[i]
            questions.append({
                "id": s.id,
                "type": "read",
                "content": s.content,
                "pronunciation": s.pronunciation,
                "meaning": s.meaning
            })

        # 2 câu viết (Cho nghĩa, viết câu thuật ngữ)
        for i in range(13, 15):
            s = selected_sentences[i]
            questions.append({
                "id": s.id,
                "type": "write",
                "content": s.content,
                "pronunciation": s.pronunciation,
                "meaning": s.meaning
            })

        random.shuffle(questions) # Trộn lẫn các loại câu hỏi
        
        return {"success": True, "questions": questions}

    @staticmethod
    def save_result(user_id, unit_id, score_percentage, completion_time):
        result = ResultUnitTest.query.filter_by(Userid=user_id, Unitid=unit_id).first()
        
        if result:
            # Chỉ cập nhật nếu phần trăm đúng cao hơn, hoặc bằng nhưng thời gian nhanh hơn
            if score_percentage > result.correctPercentage:
                result.correctPercentage = score_percentage
                result.completionTime = completion_time
            elif score_percentage == result.correctPercentage and completion_time < result.completionTime:
                result.completionTime = completion_time
        else:
            result = ResultUnitTest(
                Userid=user_id,
                Unitid=unit_id,
                correctPercentage=score_percentage,
                completionTime=completion_time
            )
            db.session.add(result)
            
        db.session.commit()
        
        return {
            "success": True, 
            "message": "Đã lưu kết quả thành công.",
            "record": {
                "score": result.correctPercentage,
                "time": result.completionTime
            }
        }

    @staticmethod
    def get_record(user_id, unit_id):
        result = ResultUnitTest.query.filter_by(Userid=user_id, Unitid=unit_id).first()
        if result:
            return {
                "score": result.correctPercentage,
                "time": result.completionTime
            }
        return None
