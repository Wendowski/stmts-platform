# Toolchain

Observed: Python 3.12.14; Node 24.22.1; npm 11.9.0. Resolved Django 5.2.19, DRF 3.18.3 and Angular 21.2.29 (supported 21 series); complete exact versions are in dependency locks.

Primary support references checked 8 November 2026:
- https://www.djangoproject.com/download/
- https://angular.dev/reference/versions
- https://v21.angular.dev/reference/releases
- https://developer.android.com/develop/ui/compose/bom
- https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html

Native target assumptions: Swift tools 6.0 / iOS 17+, Java 17 / SDK 36 / AGP 8.13.0 / Kotlin 2.2.20 / Compose BOM 2026.09.00. These configurations have not been compiled here. Native lockfiles and toolchain validation are outstanding; M0 cannot close until both clients build.
