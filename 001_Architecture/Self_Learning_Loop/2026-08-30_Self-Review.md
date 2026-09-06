## Structural API Semantics Must Be Enforced in Code

The main failure was not prompt quality. A storyboard and a temporal first
frame were assigned different meanings in the workflow, but the batch script
used the same field for both. Prompt instructions cannot reliably compensate
for a wrong API field. The durable fix is to encode asset roles in named
parameters, validate them before paid calls, and test the exact failure mode.

## Tomorrow

Resume at the corrected Neon Parcel Seedance routing. Do not rerun Shot 8
automatically: first decide whether the corrected Mini endpoint should receive
the storyboard alone as `reference_image_urls`, or a separately generated
clean start frame through `first_frame_url` only when the endpoint and shot
route explicitly require it. Preserve and archive the current v1 output if a
new revision is approved.
