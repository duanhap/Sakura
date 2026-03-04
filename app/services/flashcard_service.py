from app.extensions import db
from app.models import Flashcard, FlashcardUser

class FlashcardService:
    @staticmethod
    def get_flashcards_by_unit(unit_id):
        return Flashcard.query.filter_by(UnitId=unit_id).all()

    @staticmethod
    def get_flashcard(flashcard_id):
        return Flashcard.query.get(flashcard_id)

    @staticmethod
    def create_flashcard(unit_id, term, pronunciation, description, memory_tip):
        if not term:
            return {"success": False, "message": "Thuật ngữ không được để trống."}
        flashcard = Flashcard(
            UnitId=unit_id,
            term=term,
            pronunciation=pronunciation,
            description=description,
            memoryTip=memory_tip
        )
        db.session.add(flashcard)
        db.session.commit()
        return {"success": True, "message": "Thêm từ vựng thành công.", "flashcard": flashcard}

    @staticmethod
    def update_flashcard(flashcard_id, term, pronunciation, description, memory_tip):
        flashcard = Flashcard.query.get(flashcard_id)
        if not flashcard:
            return {"success": False, "message": "Từ vựng không tồn tại."}
        if not term:
            return {"success": False, "message": "Thuật ngữ không được để trống."}
        
        flashcard.term = term
        flashcard.pronunciation = pronunciation
        flashcard.description = description
        flashcard.memoryTip = memory_tip
        db.session.commit()
        return {"success": True, "message": "Cập nhật từ vựng thành công.", "flashcard": flashcard}

    @staticmethod
    def delete_flashcard(flashcard_id):
        flashcard = Flashcard.query.get(flashcard_id)
        if not flashcard:
            return {"success": False, "message": "Từ vựng không tồn tại."}
        db.session.delete(flashcard)
        db.session.commit()
        return {"success": True, "message": "Xóa từ vựng thành công."}

    @staticmethod
    def delete_all_flashcards(unit_id):
        # Đầu tiên xóa status của các flashcard này của user (FlashcardUser) để tránh lỗi FK
        FlashcardUser.query.filter(FlashcardUser.FlashcardId.in_(
            db.session.query(Flashcard.id).filter_by(UnitId=unit_id)
        )).delete(synchronize_session=False)

        Flashcard.query.filter_by(UnitId=unit_id).delete()
        db.session.commit()
        return {"success": True, "message": "Đã xóa toàn bộ từ vựng."}

    @staticmethod
    def process_document(unit_id, text_content):
        """
        Parse text document with format:
        1. Thuật ngữ: 你
        Cách đọc: [ nǐ ]
        Mô tả: ...
        Ví dụ: ...
        Cách nhớ: ...
        """
        import re
        
        # Split by number list like "1. Thuật ngữ:" or "1.Thuật ngữ:"
        blocks = re.split(r'\n\s*\d+\.\s*Thuật ngữ:', '\n' + text_content)
        
        flashcards_to_add = []
        for block in blocks:
            if not block.strip():
                continue
            
            lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
            term = lines[0] if lines else ""
            
            pronunciation = ""
            description = ""
            example = ""
            memory_tip = ""
            
            current_field = None
            for line in lines[1:]:
                if line.startswith("Cách đọc:"):
                    pronunciation = line.replace("Cách đọc:", "").strip()
                    current_field = "pronunciation"
                elif line.startswith("Mô tả:"):
                    description = line.replace("Mô tả:", "").strip()
                    current_field = "description"
                elif line.startswith("Ví dụ:"):
                    example = line.replace("Ví dụ:", "").strip()
                    current_field = "example"
                elif line.startswith("Cách nhớ:"):
                    memory_tip = line.replace("Cách nhớ:", "").strip()
                    current_field = "memory_tip"
                else:
                    # Append to current matching area
                    if current_field == "pronunciation":
                        pronunciation += "\n" + line
                    elif current_field == "description":
                        description += "\n" + line
                    elif current_field == "example":
                        example += "\n" + line
                    elif current_field == "memory_tip":
                        memory_tip += "\n" + line
            
            if example:
                description = f"{description}\nVí dụ: {example}"
                
            if term:
                flashcards_to_add.append(Flashcard(
                    UnitId=unit_id,
                    term=term,
                    pronunciation=pronunciation,
                    description=description,
                    memoryTip=memory_tip
                ))
        
        if flashcards_to_add:
            try:
                db.session.add_all(flashcards_to_add)
                db.session.commit()
                added = len(flashcards_to_add)
                return {"success": True, "message": f"Đã thêm {added} từ vựng từ tệp."}
            except Exception as e:
                db.session.rollback()
                return {"success": False, "message": f"Lỗi khi lưu dữ liệu: {str(e)}"}
        
        return {"success": True, "message": "Không tìm thấy từ vựng nào để thêm."}

    @staticmethod
    def get_flashcards_with_status(unit_id, user_id):
        flashcards = Flashcard.query.filter_by(UnitId=unit_id).all()
        # Fetch all statuses for this user and unit
        statuses = FlashcardUser.query.join(Flashcard).filter(
            FlashcardUser.UserId == user_id,
            Flashcard.UnitId == unit_id
        ).all()
        
        status_map = {s.FlashcardId: s.status for s in statuses}
        
        result = []
        for f in flashcards:
            result.append({
                "id": f.id,
                "term": f.term,
                "pronunciation": f.pronunciation,
                "description": f.description,
                "memoryTip": f.memoryTip,
                "status": status_map.get(f.id, "CHUA_THUOC")
            })
        return result

    @staticmethod
    def update_user_status(flashcard_id, user_id, status):
        """Update user study status for a flashcard."""
        if status not in ['CHUA_THUOC', 'THUOC']:
            return {"success": False, "message": "Trạng thái không hợp lệ."}
            
        fu = FlashcardUser.query.filter_by(FlashcardId=flashcard_id, UserId=user_id).first()
        if not fu:
            fu = FlashcardUser(FlashcardId=flashcard_id, UserId=user_id, status=status)
            db.session.add(fu)
        else:
            fu.status = status
            
        db.session.commit()
        return {"success": True, "status": fu.status}
