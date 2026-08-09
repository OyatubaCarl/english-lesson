#!/usr/bin/env python3
"""Build H071 dense Style01 video plan."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; LESSON=ROOT/'H071'; PLAN=LESSON/'planning/video_plan.json'
GROUPS=(
 (0,5,'oral_intro',3),(5,9.2,'world_intro',3),(9.2,14,'stories_continue',3),(14,20.22,'oral_written',4),
 (20.22,25,'across_lands',3),(25,31.98,'old_expression',4),(31.98,34.84,'homer',2),(34.84,37.54,'shakespeare',2),
 (37.54,38.89,'tolstoy',1),(38.89,40.24,'murasaki',1),(40.24,47.9,'worldview',5),(47.9,51.62,'why_literature',2),
 (51.62,57,'another_life',3),(57,62,'widen_world',3),(62,66,'character_joy',3),(66,69.997,'character_conflict',3),
 (69.997,73.22,'soseki',2),(73.22,76.44,'dostoevsky',2),(76.44,81.72,'dark_heart',3),(81.72,89.3,'hard_question',5),
 (89.3,97.52,'poetry',5),(97.52,102.581,'single_moment',3),(102.581,108.758,'metaphor',4),(108.758,114,'media_coexist',3),
 (114,119.28,'literature_remains',3),(119.28,125,'quiet_reading',4),(125,131.076,'self_dialogue',4),(131.076,137,'reader_writer',4),
 (137,142.04,'quiet_power',3),(142.04,147.5,'outro_begin',3),(147.5,154.640167,'outro_final',4),
)
def main()->None:
 p=json.loads(PLAN.read_text()); scenes=[]
 for a,b,prefix,count in GROUPS:
  imgs=sorted((LESSON/'scenes/final_style01').glob(f'*_{prefix}_*.png'))
  if len(imgs)!=count:raise RuntimeError(f'{prefix}: {len(imgs)} != {count}')
  gap=(b-a)/count
  for i,img in enumerate(imgs):scenes.append({'start':round(a+gap*i,3),'image':str(img.relative_to(LESSON)),'purpose':prefix})
 gaps=[float(r['start'])-float(l['start']) for l,r in zip(scenes,scenes[1:])]+[float(p['duration'])-float(scenes[-1]['start'])]
 if min(gaps)<1.3 or max(gaps)>1.9:raise RuntimeError((len(scenes),min(gaps),max(gaps)))
 p['scenes']=scenes;p['qa_status']='READY_TO_RENDER_STYLE01_FACT_CHECKED';p['output_name']='h071_adopted_song_cinematic_v1.mp4'
 PLAN.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
 print(f'H071 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s max {max(gaps):.3f}s')
if __name__=='__main__':main()
