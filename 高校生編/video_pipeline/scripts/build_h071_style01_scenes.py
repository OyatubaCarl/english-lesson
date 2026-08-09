#!/usr/bin/env python3
"""Create H071 dense Style01 crops from the accepted masters."""
from __future__ import annotations
import shutil, subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; REF=ROOT/'H071/scenes/character_refs'; OUT=ROOT/'H071/scenes/final_style01'
@dataclass(frozen=True)
class Series: master:str; prefix:str; crops:tuple[str|None,...]
F=None; WL='1420x799+0+20'; WR='1420x799+252+20'; ML='1320x743+0+55'; MR='1320x743+352+55'; L='1180x664+0+90'; R='1180x664+492+90'; C='1180x664+246+90'; CL='1100x619+80+110'; CR='1100x619+492+110'; DL='920x518+40+130'; DC='920x518+376+130'; DR='920x518+712+130'
SERIES=(
 Series('oral_story_circle_master.png','oral_intro',(F,ML,C)),
 Series('world_storytelling_master.png','world_intro',(F,MR,C)),
 Series('oral_story_circle_master.png','stories_continue',(F,WL,CR)),
 Series('ancient_story_transmission_master.png','oral_written',(F,WL,MR,C)),
 Series('world_storytelling_master.png','across_lands',(F,MR,C)),
 Series('ancient_story_transmission_master.png','old_expression',(F,ML,MR,DC)),
 Series('homeric_bard_master.png','homer',(F,R)),
 Series('shakespeare_globe_master.png','shakespeare',(F,R)),
 Series('tolstoy_writing_master.png','tolstoy',(C,)),
 Series('murasaki_writing_master.png','murasaki',(C,)),
 Series('literary_worldview_master.png','worldview',(F,WL,MR,R,C)),
 Series('student_literature_question_master.png','why_literature',(F,C)),
 Series('reading_another_life_master.png','another_life',(F,WL,C)),
 Series('literary_worldview_master.png','widen_world',(F,MR,C)),
 Series('character_joy_master.png','character_joy',(F,ML,C)),
 Series('character_sorrow_conflict_master.png','character_conflict',(F,MR,C)),
 Series('soseki_kokoro_master.png','soseki',(F,C)),
 Series('dostoevsky_crime_punishment_master.png','dostoevsky',(F,C)),
 Series('novel_dark_heart_master.png','dark_heart',(F,ML,C)),
 Series('reader_faces_question_master.png','hard_question',(F,WL,MR,R,C)),
 Series('poetry_part_master.png','poetry',(F,WL,MR,DC,C)),
 Series('single_moment_essence_master.png','single_moment',(F,C,DC)),
 Series('metaphor_symbol_master.png','metaphor',(F,WL,MR,C)),
 Series('film_internet_books_master.png','media_coexist',(F,MR,C)),
 Series('film_internet_books_master.png','literature_remains',(F,R,DR)),
 Series('quiet_alone_reading_master.png','quiet_reading',(F,WL,MR,C)),
 Series('quiet_alone_reading_master.png','self_dialogue',(F,ML,CR,C)),
 Series('reader_writer_dialogue_master.png','reader_writer',(F,WL,MR,C)),
 Series('reader_writer_dialogue_master.png','quiet_power',(F,R,C)),
 Series('library_student_outro_master.png','outro_begin',(F,MR,C)),
 Series('library_student_outro_master.png','outro_final',(F,WL,MR,C)),
)
EXPECTED=sum(len(s.crops) for s in SERIES)
def render(src:Path,dst:Path,crop:str|None)->None:
 if dst.is_file() and dst.stat().st_size:return
 if crop is None: shutil.copyfile(src,dst); return
 subprocess.run(['magick',str(src),'-crop',crop,'+repage','-resize','1672x941^','-gravity','center','-extent','1672x941',str(dst)],check=True)
def main()->None:
 OUT.mkdir(parents=True,exist_ok=True); expected=[]; n=1
 for s in SERIES:
  src=REF/s.master
  if not src.is_file():raise FileNotFoundError(src)
  for i,crop in enumerate(s.crops,1):
   dst=OUT/f'{n:03d}_{s.prefix}_{i:02d}.png'; render(src,dst,crop); expected.append(dst); n+=1
 actual=sorted(OUT.glob('[0-9][0-9][0-9]_*.png'))
 if actual!=expected:raise RuntimeError(f'H071 scene mismatch actual={len(actual)} expected={EXPECTED}')
 print(f'H071 final_style01 files verified: {EXPECTED}')
if __name__=='__main__':main()
