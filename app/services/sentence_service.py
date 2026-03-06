from app.extensions import db
from app.models import Sentence
import re

class SentenceService:
    @staticmethod
    def get_sentences_by_unit(unit_id):
        return Sentence.query.filter_by(UnitId=unit_id).all()

    @staticmethod
    def get_sentence(sentence_id):
        return Sentence.query.get(sentence_id)

    @staticmethod
    def create_sentence(unit_id, content, pronunciation, meaning):
        if not content:
            return {"success": False, "message": "Nội dung không được để trống."}
        sentence = Sentence(
            UnitId=unit_id,
            content=content,
            pronunciation=pronunciation,
            meaning=meaning
        )
        db.session.add(sentence)
        db.session.commit()
        return {"success": True, "message": "Thêm câu thành công.", "sentence": sentence}

    @staticmethod
    def update_sentence(sentence_id, content, pronunciation, meaning):
        sentence = Sentence.query.get(sentence_id)
        if not sentence:
            return {"success": False, "message": "Câu không tồn tại."}
        if not content:
            return {"success": False, "message": "Nội dung không được để trống."}
        
        sentence.content = content
        sentence.pronunciation = pronunciation
        sentence.meaning = meaning
        db.session.commit()
        return {"success": True, "message": "Cập nhật câu thành công.", "sentence": sentence}

    @staticmethod
    def delete_sentence(sentence_id):
        sentence = Sentence.query.get(sentence_id)
        if not sentence:
            return {"success": False, "message": "Câu không tồn tại."}
        db.session.delete(sentence)
        db.session.commit()
        return {"success": True, "message": "Xóa câu thành công."}

    @staticmethod
    def delete_all_sentences(unit_id):
        Sentence.query.filter_by(UnitId=unit_id).delete()
        db.session.commit()
        return {"success": True, "message": "Đã xóa toàn bộ câu."}

    @staticmethod
    def process_document(unit_id, text_content):
        """
        Parse text document with format:
        Thuật ngữ: 你好 (Nǐ hǎo) Nghĩa: Xin chào.
        """
        lines = text_content.strip().split('\n')
        
        sentences_to_add = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 1. Thử định dạng mới: Thuật ngữ: <content> Cách đọc: [ <pronunciation> ] Nghĩa: <meaning>
            match_new = re.search(r'Thuật ngữ:\s*(.+?)\s*Cách đọc:\s*\[\s*(.*?)\s*\]\s*Nghĩa:\s*(.*)', line, re.IGNORECASE)
            
            # 2. Thử định dạng cũ: Thuật ngữ: <content> (<pronunciation>) Nghĩa: <meaning>
            match_old = re.search(r'Thuật ngữ:\s*(.+?)(?:\s*\((.*?)\))?\s*Nghĩa:\s*(.*)', line, re.IGNORECASE)
            
            if match_new:
                content = match_new.group(1).strip()
                pronunciation = match_new.group(2).strip()
                meaning = match_new.group(3).strip()
            elif match_old:
                content = match_old.group(1)
                # Xử lý trường hợp content bị dính "Cách đọc" nếu regex cũ bắt nhầm (dù khó xảy ra với logic hiện tại)
                if "Cách đọc:" in content: continue 
                content = content.strip()
                pronunciation = match_old.group(2).strip() if match_old.group(2) else ""
                meaning = match_old.group(3).strip()
            else:
                continue

            sentences_to_add.append(Sentence(
                UnitId=unit_id,
                content=content,
                pronunciation=pronunciation,
                meaning=meaning
            ))
        
        if sentences_to_add:
            try:
                db.session.add_all(sentences_to_add)
                db.session.commit()
                added = len(sentences_to_add)
                return {"success": True, "message": f"Đã thêm {added} câu từ tệp."}
            except Exception as e:
                db.session.rollback()
                return {"success": False, "message": f"Lỗi khi lưu dữ liệu: {str(e)}"}

        return {"success": True, "message": "Không tìm thấy câu nào để thêm."}
