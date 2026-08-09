# The single swap point for the Foley A/B test: change this one line, nothing else,
# to switch the default model once Tony picks a winner.
FOLEY_MODEL = "mirelo"

FOLEY_MODELS = {
    "mirelo": "mirelo-ai/sfx-v1/video-to-audio",
    "sonilo": "sonilo/v1/video-to-sfx",
}
