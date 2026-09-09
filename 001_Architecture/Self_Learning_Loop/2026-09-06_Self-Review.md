## Thumbnail demographic correction

- A production-specific Grandma direction was incorrectly close to becoming a
  reusable default. The correct abstraction is content-first demographic
  matching, with variation allowed only within the people represented in the
  source video.

## Compilation metadata tags are now a pipeline default

- A one-off tag list became a reusable requirement: every Neon Parcel long-form
  title/description pass must also produce a comma-separated tag string under
  500 characters.
- The reliable pattern is collection-level search intent plus a small number
  of plausible common misspellings, while avoiding unsupported authenticity or
  specific-event claims.
