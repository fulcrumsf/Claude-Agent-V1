# Packet Manifest Schema

The manifest is the packet's machine-readable source of truth. Unknown project-specific fields may be preserved under `extensions`, but the core fields below should remain stable.

```json
{
  "schema_version": "1.0",
  "project_id": "project-name",
  "scene_id": "scene-001",
  "scene_purpose": "What this scene accomplishes",
  "status": "draft",
  "version": 1,
  "parent_version": null,
  "revision_reason": null,
  "duration_s": 12.0,
  "visual_style": "Caller-supplied style guidance",
  "characters": [],
  "wardrobe_changes": [],
  "props": [],
  "environment": {},
  "beats": [],
  "assets": [
    {
      "id": "character-main-master",
      "role": "master_character",
      "path": "References/Characters/Main-Master.png",
      "version": 1,
      "reference_ordinal": "@Image1",
      "required": true,
      "notes": "Persistent identity reference"
    }
  ],
  "validation": {
    "blocking_findings": [],
    "warnings": [],
    "checked_at": null
  },
  "extensions": {}
}
```

## Status Values

- `draft` — packet is being assembled
- `needs_revision` — blocking validation findings exist
- `ready_for_review` — packet is complete enough for the consuming pipeline's review gate
- `approved` — consuming pipeline recorded approval
- `superseded` — replaced by a later packet version
