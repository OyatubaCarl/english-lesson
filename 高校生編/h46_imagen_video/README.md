# H46 ImageGen video trial

- Final video: `output/h46_democracy_constitution_imagen_cinematic.mp4`
- Adopted song: <https://suno.com/s/YyNYeSPYvPCL8USO>
- Audio duration: 131.800 seconds
- Visuals: eight new Codex ImageGen scenes
- Caption timing: aligned from two independent Whisper-family recognizers
- English: exact lesson lyrics; Japanese: concise instructional translation
- Scene policy: cinematic outdoor views, grounded and natural indoor rooms

## Build

```bash
python3 scripts/build_video.py
```

The older picture-book trial images and the indoor images with forced scenic skies remain in `scenes/` for comparison, but the build plan does not reference them.
