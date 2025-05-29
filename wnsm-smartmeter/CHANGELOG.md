# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.2.2](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.2.1...v0.2.2) (2025-05-29)


### Bug Fixes

* Fix parameter name issue in bewegungsdaten method call
* Add fallback for different vienna-smartmeter library versions

### [0.2.1](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.27...v0.2.1) (2025-05-29)


### Features

* update Wiener Netze Smartmeter add-on to use vienna-smartmeter library with PKCE authentication ([a8f2fad](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/a8f2fadddf873c4762872695a29c685970b3daf1))

## [0.2.0](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.27...v0.2.0) (2025-05-30)


### ⚠ BREAKING CHANGES

* **api:** The addon now uses the vienna-smartmeter library with PKCE authentication support

### Features

* **api:** Switch to vienna-smartmeter library for API communication ([#1](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/issues/1))
* **auth:** Add support for PKCE authentication required by Wiener Netze API since May 2025
* **config:** Add HISTORY_DAYS option to control how much historical data is fetched
* **mock:** Improve mock data generation for testing without API access

### Bug Fixes

* **login:** Fix login issues with Wiener Netze API by implementing PKCE authentication
* **error:** Improve error handling and logging for API communication failures
* **docs:** Update documentation with new configuration options and troubleshooting tips

### [0.1.27](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.26...v0.1.27) (2025-05-29)


### Features

* **api:** improve URL handling and add headers for API requests ([7650242](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/76502424cac88148a4a02c317f859bf79feca8e7))

### [0.1.27](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.26...v0.1.27) (2025-05-29)


### Bug Fixes

* **api:** fix URL joining for API endpoints to properly include base path
* **api:** update API headers to include Accept and Content-Type
* **api:** remove leading slashes from endpoint definitions for proper URL construction

### [0.1.26](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.25...v0.1.26) (2025-05-29)


### Features

* **config:** add USE_MOCK_DATA option for testing and development ([82be8f5](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/82be8f52b51eadf13b27f02490e936795b1f2908))

### [0.1.26](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.25...v0.1.26) (2025-05-29)


### Features

* **config:** add USE_MOCK_DATA option for testing and development ([82be8f5](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/82be8f52b51eadf13b27f02490e936795b1f2908))

### [0.1.25](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.24...v0.1.25) (2025-05-29)


### Features

* **api:** enhance data fetching and processing logic for statistics ([5b7f814](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/5b7f8141cce8a92adb448c1cf9d513c75f32ae84))

### [0.1.24](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.23...v0.1.24) (2025-05-29)


### Features

* **api:** add OAUTH_SCOPE constant and include it in token request parameters ([a9c5c34](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/a9c5c342fa7fd5f7d82ec9b13f0b3f89d62bb814))

### [0.1.23](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.22...v0.1.23) (2025-05-29)


### Features

* **api:** implement mock data responses for API endpoints and add OpenAPI schema ([2710158](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/27101580eafae6aa0dac896bd84b63e6144615b9))

### [0.1.22](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.21...v0.1.22) (2025-05-29)

### [0.1.21](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.20...v0.1.21) (2025-05-29)

### [0.1.20](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.19...v0.1.20) (2025-05-29)

### [0.1.19](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.18...v0.1.19) (2025-05-29)

### [0.1.18](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.17...v0.1.18) (2025-05-29)

### [0.1.17](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.16...v0.1.17) (2025-05-29)

### [0.1.16](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.15...v0.1.16) (2025-05-29)

### [0.1.15](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.14...v0.1.15) (2025-05-29)

### [0.1.14](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.13...v0.1.14) (2025-05-29)

### [0.1.13](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.12...v0.1.13) (2025-05-29)

### [0.1.12](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.11...v0.1.12) (2025-05-29)

### [0.1.11](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.10...v0.1.11) (2025-05-21)

### [0.1.10](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.9...v0.1.10) (2025-05-21)

### [0.1.9](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.8...v0.1.9) (2025-05-21)

### [0.1.8](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.7...v0.1.8) (2025-05-21)

### [0.1.7](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.6...v0.1.7) (2025-05-21)

### [0.1.6](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.5...v0.1.6) (2025-05-21)


### Features

* enhance MQTT configuration handling and add message publishing functions ([8c1e229](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/8c1e229e5b53b82e0059d1459023ae10d650a9b6))

### [0.1.5](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.4...v0.1.5) (2025-05-21)

### [0.1.4](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.3...v0.1.4) (2025-05-21)


### Features

* add fetch_bewegungsdaten function to retrieve energy consumption data from Wiener Netze API ([7f56d7d](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/7f56d7df6cd2f3e08cf8e5f35a86e2dffded5fc9))
* initialize __init__.py for wnsm_sync module ([1ce2a46](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/commit/1ce2a469995e366426fe7cf9b1df3123a152aa0b))

### [0.1.3](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.2...v0.1.3) (2025-05-21)

### [0.1.2](https://github.com/ZakiZtraki/haos-addon-wnsm-dev/compare/v0.1.1...v0.1.2) (2025-05-21)
