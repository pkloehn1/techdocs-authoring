## Problem

Session timeouts are not configurable, so every deployment inherits the
30-minute default whether or not it suits the tenant.

## Proposed

Read the timeout from configuration, falling back to 30 minutes.

## Acceptance criteria

- [ ] The timeout is read from configuration.
- [ ] A tenant with no configured value still gets 30 minutes.
- [ ] Support has confirmed the three largest tenants are happy with their new
      values after the change has been live for a month.
- [ ] The follow-up work to expose this in the admin UI is complete.
