# Integrations

## Provider Integrations
- kie.ai is the preferred video-generation route according to `TOOLBOX.md`.
- Seedance Mini uses the market API wrapper documented in `001_Architecture/Tools/Video-Generation/`.
- Public image hosting is used when providers require HTTPS reference URLs.
- GPT-Image-2 may be routed through kie.ai or direct OpenAI depending on capability and price requirements.

## Workspace Integrations
- Generation records are persisted in production `Data/Generation_Log.json` files.
- Production checkpoints are persisted in `Data/Checkpoints/Checkpoint_State.json` and append-only decision logs.
- Storyboards, prompts, images, clips, and archives are linked by shot ID and version.

## Integration Boundary for the Planned Feature
- The storyboard QA layer should validate before any Seedance task is submitted.
- It should pass a validated storyboard artifact and an evidence record downstream.
- It should not silently call paid providers beyond the configured maximum candidate count.
- A failed three-candidate run must produce a human-review flag instead of a video request.
