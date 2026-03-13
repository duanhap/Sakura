import random
from app.extensions import db
from app.models import Sentence, ResultUnitTest, Unit, Flashcard, Course

class TestService:
    @staticmethod
    def _segment_text(text, flash_terms, lang='ja'):
        """
        Phân tách văn bản thành các cụm từ dựa trên danh sách flashcard đã cho (greedy match).
        Những phần không khớp sẽ được nhóm lại thành các cụm từ ngắn thay vì từng ký tự để dễ sắp xếp
        và tránh gây mệt mỏi cho người dùng.
        """
        # Sắp xếp các cụm từ theo độ dài giảm dần để ưu tiên các từ dài nhất (greedy)
        sorted_terms = sorted(list(flash_terms), key=len, reverse=True)
        
        punctuation = '.,;!?。，！？、'
        result = []
        i = 0
        
        # Kiểm tra nếu là ngôn ngữ CJK (Trung, Nhật, Hàn)
        lang_code = lang.lower() if lang else 'ja'
        is_cjk = any(c in lang_code for c in ['ja', 'zh', 'ko'])
        
        while i < len(text):
            char = text[i]
            # Bỏ qua khoảng trắng hoặc dấu câu
            if not char.strip() or char in punctuation:
                i += 1
                continue
            
            found = False
            for term in sorted_terms:
                if text.startswith(term, i):
                    result.append(term)
                    i += len(term)
                    found = True
                    break
            
            if not found:
                if not is_cjk:
                    # Đối với ngôn ngữ có dấu cách (en, vi...), lấy toàn bộ từ tiếp theo
                    j = i
                    while j < len(text) and text[j].strip() and text[j] not in punctuation:
                        # Kiểm tra xem có flashcard nào bắt đầu giữa chừng ko
                        inner_found = False
                        for term in sorted_terms:
                            if text.startswith(term, j):
                                inner_found = True
                                break
                        if inner_found: break
                        j += 1
                    segment = text[i:j]
                    if segment:
                        result.append(segment)
                    i = j
                else:
                    # Đối với tiếng Nhật/Trung, nhóm các ký tự lại (tối đa 3-4 ký tự)
                    # Điều này giúp giảm số lượng block cần sắp xếp
                    start = i
                    j = i + 1
                    # Nhóm tối đa 3-4 ký tự hoặc cho đến khi gặp flashcard/dấu câu
                    while j < len(text) and j < i + 4:
                        if not text[j].strip() or text[j] in punctuation:
                            break
                        
                        # Kiểm tra nếu có flashcard bắt đầu từ vị trí j
                        inner_found = False
                        for term in sorted_terms:
                            if text.startswith(term, j):
                                inner_found = True
                                break
                        if inner_found:
                            break
                        j += 1
                    
                    result.append(text[i:j])
                    i = j
                
        return result

    @staticmethod
    def generate_test(unit_id):
        unit = Unit.query.get(unit_id)
        if not unit:
             return {"success": False, "message": "Bài học không tồn tại."}

        sentences = Sentence.query.filter_by(UnitId=unit_id).all()
        if not sentences:
            return {"success": False, "message": "Không có câu nào trong bài học này để tạo bài kiểm tra."}

        # Lấy ngôn ngữ của khóa học hiện tại
        current_lang = unit.course.languageCourse
        
        # Lấy tất cả flashcard thuộc ngôn ngữ này trong hệ thống để làm từ điển phân tách câu
        # Điều này giúp giữ nguyên các "cụm từ" có ý nghĩa thay vì tách rời từng chữ cái
        flashcards = db.session.query(Flashcard.term).join(Unit).join(Course).filter(Course.languageCourse == current_lang).all()
        flash_terms = set(f[0] for f in flashcards if f[0])

        # Phân tách tất cả các câu trong bài học thành các đơn vị (tokens)
        all_tokens = set()
        segmented_sentences_map = {} # sentence_id -> tokens

        for s in sentences:
            tokens = TestService._segment_text(s.content, flash_terms, current_lang)
            segmented_sentences_map[s.id] = tokens
            for token in tokens:
                all_tokens.add(token)
        
        all_tokens_list = list(all_tokens)

        # Chọn ngẫu nhiên 15 câu (có thể lặp lại nếu số câu < 15, nhưng cố gắng unique nếu có thể)
        selected_sentences = random.choices(sentences, k=15) if len(sentences) < 15 else random.sample(sentences, 15)
        
        # Xáo trộn để bắt đầu phân loại
        random.shuffle(selected_sentences)
        
        questions = []
        
        # 5 câu nghe (Mục tiêu chính: Sắp xếp các cụm từ/từ thay vì chữ cái rác)
        for i in range(5):
            s = selected_sentences[i]
            tokens = segmented_sentences_map[s.id]
            
            distractors = []
            available_distractors = [t for t in all_tokens_list if t not in tokens]
            if available_distractors:
                distractors = random.sample(available_distractors, min(4, len(available_distractors)))
            
            options = tokens + distractors
            random.shuffle(options)
            
            questions.append({
                "id": s.id,
                "type": "listen",
                "content": s.content,
                "pronunciation": s.pronunciation,
                "meaning": s.meaning,
                "options": options,
                "answer": tokens # Trả về mảng tokens để check logic ở JS
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
