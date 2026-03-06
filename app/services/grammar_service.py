from app.extensions import db
from app.models import Grammar
import re

class GrammarService:
    @staticmethod
    def get_grammars_by_unit(unit_id):
        return Grammar.query.filter_by(UnitId=unit_id).all()

    @staticmethod
    def get_grammar(grammar_id):
        return Grammar.query.get(grammar_id)

    @staticmethod
    def create_grammar(unit_id, title, content):
        grammar = Grammar(UnitId=unit_id, title=title, content=content)
        db.session.add(grammar)
        db.session.commit()
        return {"success": True, "message": "Thêm ngữ pháp thành công.", "grammar": grammar}

    @staticmethod
    def update_grammar(grammar_id, title, content):
        grammar = Grammar.query.get(grammar_id)
        if not grammar:
            return {"success": False, "message": "Ngữ pháp không tồn tại."}
        
        grammar.title = title
        grammar.content = content
        db.session.commit()
        return {"success": True, "message": "Cập nhật ngữ pháp thành công.", "grammar": grammar}

    @staticmethod
    def delete_grammar(grammar_id):
        grammar = Grammar.query.get(grammar_id)
        if not grammar:
            return {"success": False, "message": "Ngữ pháp không tồn tại."}
        
        db.session.delete(grammar)
        db.session.commit()
        return {"success": True, "message": "Xóa ngữ pháp thành công."}

    @staticmethod
    def delete_all_grammars(unit_id):
        Grammar.query.filter_by(UnitId=unit_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def process_grammar_text(unit_id, text_content):
        """
        Parse text with format:
        1. Title: ...
        Content lines...
        2. Title: ...
        ...
        """
        # Split by "Number. " pattern at the start of lines
        items = re.split(r'\n\s*\d+\.\s*', '\n' + text_content)
        
        grammars_added = 0
        for item in items:
            if not item.strip():
                continue
            
            lines = item.strip().split('\n')
            if not lines:
                continue
            
            # The first line of the block is the title
            title = lines[0].strip()
            # The rest is the content
            content = '\n'.join(lines[1:]).strip()
            
            if title:
                grammar = Grammar(
                    UnitId=unit_id,
                    title=title,
                    content=content
                )
                db.session.add(grammar)
                grammars_added += 1
        
        db.session.commit()
        return grammars_added
