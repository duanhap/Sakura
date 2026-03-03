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
        
        added = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Thuật ngữ: <content> (<pronunciation>) Nghĩa: <meaning>
            match = re.search(r'Thuật ngữ:\s*(.+?)(?:\s*\((.*?)\))?\s*Nghĩa:\s*(.*)', line, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                pronunciation = match.group(2).strip() if match.group(2) else ""
                meaning = match.group(3).strip()
                
                SentenceService.create_sentence(unit_id, content, pronunciation, meaning)
                added += 1
                
        return {"success": True, "message": f"Đã thêm {added} câu từ tệp."}
