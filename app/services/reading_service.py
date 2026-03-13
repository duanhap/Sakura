from app.extensions import db
from app.models import Reading
import re

class ReadingService:
    @staticmethod
    def get_readings_by_unit(unit_id):
        return Reading.query.filter_by(UnitId=unit_id).all()

    @staticmethod
    def get_reading(reading_id):
        return Reading.query.get(reading_id)

    @staticmethod
    def create_reading(unit_id, title, content, pronunciation, translation, video_url=None):
        reading = Reading(
            UnitId=unit_id, 
            title=title, 
            content=content, 
            pronunciation=pronunciation, 
            translation=translation,
            videoUrl=video_url
        )
        db.session.add(reading)
        db.session.commit()
        return {"success": True, "message": "Thêm bài đọc thành công.", "reading": reading}

    @staticmethod
    def update_reading(reading_id, title, content, pronunciation, translation, video_url=None):
        reading = Reading.query.get(reading_id)
        if not reading:
            return {"success": False, "message": "Bài đọc không tồn tại."}
        
        reading.title = title
        reading.content = content
        reading.pronunciation = pronunciation
        reading.translation = translation
        reading.videoUrl = video_url
        db.session.commit()
        return {"success": True, "message": "Cập nhật bài đọc thành công.", "reading": reading}


    @staticmethod
    def delete_reading(reading_id):
        reading = Reading.query.get(reading_id)
        if not reading:
            return {"success": False, "message": "Bài đọc không tồn tại."}
        
        db.session.delete(reading)
        db.session.commit()
        return {"success": True, "message": "Xóa bài đọc thành công."}

    @staticmethod
    def delete_all_readings(unit_id):
        Reading.query.filter_by(UnitId=unit_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def process_reading_text(unit_id, text_content):
        """
        Parse text with format:
        Tiêu đề: ...
        Thuật ngữ: ...
        Cách đọc: ...
        Dịch: ...
        """
        # If there are multiple readings, let's try to split by "Tiêu đề:"
        parts = re.split(r'\n?\s*tiêu đề\s*:\s*', text_content, flags=re.IGNORECASE)
        
        readings_added = 0
        for part in parts:
            if not part.strip():
                continue
            
            # Extract title (it's the first line after splitting or before first keyword)
            # Find the first keyword position
            keywords = [r'thuật ngữ\s*:', r'cách đọc\s*:', r'dịch\s*:']
            first_keyword_pos = len(part)
            for kw in keywords:
                match = re.search(kw, part, re.IGNORECASE)
                if match and match.start() < first_keyword_pos:
                    first_keyword_pos = match.start()
            
            title_segment = part[:first_keyword_pos].strip()
            title = title_segment.split('\n')[0].strip() if title_segment else ""
            
            # Extract sections
            content_match = re.search(r'thuật ngữ\s*:\s*(.*?)(?=cách đọc\s*:|dịch\s*:|$)', part, re.IGNORECASE | re.DOTALL)
            pron_match = re.search(r'cách đọc\s*:\s*(.*?)(?=thuật ngữ\s*:|dịch\s*:|$)', part, re.IGNORECASE | re.DOTALL)
            trans_match = re.search(r'dịch\s*:\s*(.*?)(?=thuật ngữ\s*:|cách đọc\s*:|$)', part, re.IGNORECASE | re.DOTALL)
            
            content = content_match.group(1).strip() if content_match else ""
            pronunciation = pron_match.group(1).strip() if pron_match else ""
            translation = trans_match.group(1).strip() if trans_match else ""
            
            if title and content:
                reading = Reading(
                    UnitId=unit_id,
                    title=title,
                    content=content,
                    pronunciation=pronunciation,
                    translation=translation
                )
                db.session.add(reading)
                readings_added += 1
        
        db.session.commit()
        return readings_added

    @staticmethod
    def process_srt_content(reading_id, srt_text):
        """
        Parse SRT content and save as subtitles.
        Try to match pronunciation and translation from current Unit context.
        """
        from app.models import ReadingSubtitle, Sentence, Flashcard
        reading = Reading.query.get(reading_id)
        if not reading:
            return 0
        
        # Helper to convert SRT time (00:00:14,000) to milliseconds
        def time_to_ms(t_str):
            t_str = t_str.strip().replace(',', '.')
            parts = t_str.split(':')
            h = int(parts[0])
            m = int(parts[1])
            s_ms = float(parts[2])
            return int((h * 3600 + m * 60 + s_ms) * 1000)

        # Clear existing subtitles
        ReadingSubtitle.query.filter_by(ReadingId=reading_id).delete()
        
        # Get Unit context for matching
        unit_id = reading.UnitId
        sentences = Sentence.query.filter_by(UnitId=unit_id).all()
        flashcards = Flashcard.query.filter_by(UnitId=unit_id).all()
        
        # Improved splitting for better matching even when content is a paragraph
        def split_by_sentences(text):
            if not text: return []
            # Split by common markers but keep the marker if possible, or just split
            # Actually, splitting by punctuation is safer
            parts = re.split(r'([。！？\n])', text)
            sentences = []
            for i in range(0, len(parts)-1, 2):
                sentences.append((parts[i] + parts[i+1]).strip())
            if len(parts) % 2 == 1 and parts[-1].strip():
                sentences.append(parts[-1].strip())
            return [s for s in sentences if s]
            
        reading_lines = split_by_sentences(reading.content)
        pron_lines = split_by_sentences(reading.pronunciation or "")
        trans_lines = split_by_sentences(reading.translation or "")
        
        # If the number of lines don't match exactly, fallback to line-by-line if available
        if not (len(reading_lines) == len(pron_lines) == len(trans_lines)):
            # Try simple line split if it's more consistent
            simple_content = [l.strip() for l in reading.content.split('\n') if l.strip()]
            simple_pron = [l.strip() for l in (reading.pronunciation or "").split('\n') if l.strip()]
            simple_trans = [l.strip() for l in (reading.translation or "").split('\n') if l.strip()]
            
            if len(simple_content) == len(simple_pron) == len(simple_trans):
                reading_lines = simple_content
                pron_lines = simple_pron
                trans_lines = simple_trans

        
        # Normalize line endings and split blocks
        srt_text = srt_text.replace('\r\n', '\n').strip()
        blocks = re.split(r'\n\s*\n', srt_text)
        
        subs_added = 0
        for block in blocks:
            # Clean lines in block
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if len(lines) < 2:
                continue
            
            # Find timestamp line
            ts_idx = -1
            for i, line in enumerate(lines):
                if '-->' in line:
                    ts_idx = i
                    break
            
            if ts_idx == -1:
                continue
            
            try:
                ts_line = lines[ts_idx]
                ts_parts = ts_line.split('-->')
                start_ms = time_to_ms(ts_parts[0])
                end_ms = time_to_ms(ts_parts[1])
                content = ' '.join(lines[ts_idx+1:]).strip()
            except Exception:
                continue
            
            if not content:
                continue

            # Fuzzy matching normalization
            def norm(text):
                return re.sub(r'[、。！？\.\!\?\s]', '', text or "")

            norm_content = norm(content)
            
            pron = ""
            trans = ""
            
            # 1. Match with Reading's internal lines
            for i, r_line in enumerate(reading_lines):
                if norm(r_line) == norm_content:
                    if i < len(pron_lines): pron = pron_lines[i]
                    if i < len(trans_lines): trans = trans_lines[i]
                    break
            
            # 2. Match with sentences
            if not trans:
                for s in sentences:
                    if norm(s.content) == norm_content:
                        pron = s.pronunciation
                        trans = s.meaning
                        break
            
            # 3. Match with flashcards
            if not trans:
                for f in flashcards:
                    if norm(f.term) == norm_content:
                        pron = f.pronunciation
                        trans = f.description
                        break
 
            # 4. Partial matching
            if not trans:
                for s in sentences:
                    s_norm = norm(s.content)
                    if s_norm and (norm_content in s_norm or s_norm in norm_content):
                        pron = s.pronunciation
                        trans = s.meaning
                        break

            # Debug log
            if not pron or not trans:
                print(f"DEBUG: No match for '{content}' (norm: '{norm_content}')")
                print(f"DEBUG: Reading lines checked: {len(reading_lines)}")

            sub = ReadingSubtitle(
                ReadingId=reading_id,
                startTime=start_ms,
                endTime=end_ms,
                content=content,
                pronunciation=pron,
                translation=trans
            )
            db.session.add(sub)
            subs_added += 1
            
        db.session.commit()
        print(f"DEBUG: Total subtitles added: {subs_added}")
        return subs_added



