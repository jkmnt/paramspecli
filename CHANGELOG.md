# Changelog

## [Unreleased]

## [0.3.0]

## Added

- `custom_action` brings the uniform handling of, well, custom actions
- `const`s are allowed to be mixed (once) with other options for more composability
- `const`s supports dynamic loads - the missing piece in env/toml support
- [Docs] Recipes on shell completion and toml load

## Changed

- `Const` is an alias for the `const` now for compatibility
- Repeated options are allowed to have a defaults. These defaults behave as in normal options, i.e. replaced, not appended/expanded.
  If not set, default is `None`

## [0.2.2]

### Changed

- Cosmetic fixes

### Added

- Allow parsing with unknown args. Controlled by the Config option.

### Fixed

- Do not invent option metavar if there are choices set.
  In md doc, such options are shown with the _CHOICES_ metavar now.

## [0.2.1]

### Added

- Initial release
