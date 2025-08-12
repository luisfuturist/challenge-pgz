### **Proposal: A CLI Tool for Automated Release Versioning**

This document outlines a proposal for a command-line interface (CLI) tool on top of `python-semantic-release` designed to automate and manage the release process for our game. The tool will enforce the versioning strategy defined in the STRATEGY.md document, ensuring that releases adhere to the defined lifecycle stages: Prototype, Early Access, Early Stable, and Stable.

The primary goal of this CLI is to prevent human error during the versioning process, providing a guided, menu-driven interface that only presents valid release options based on the current project status.

Noop will be the default mode, unless you confirm the release.

#### **Core Functionality**

1. **Version Detection:** The CLI will first read the pyproject.toml file to retrieve the current version string. It will parse this string to identify the MAJOR, MINOR, PATCH, and PRERELEASE components.  
2. **Stage Identification:** Based on the parsed version, the tool will automatically determine the current release stage:  
   * **Prototype:** If the version string includes a \-next.PRERELEASE suffix and below \`v0.1.0\` (e.g., v0.1.0-next.1).  
   * **Early Access:** If the version is below v1.0.0 and does not have a prerelease suffix (e.g., v0.2.0).  
   * **Early Stable:** If the version is v1.0.x (e.g., v1.0.2).  
   * **Stable:** If the version is v1.1.0 or higher (e.g., v1.2.0).  
3. **Menu-Driven Interface:** The CLI will present a clear, interactive menu to the user, displaying only the valid next-version options for the current stage.  
4. **Version Update:** Upon user selection, the CLI will update the version string in pyproject.toml and potentially execute other pre-release commands (like running tests or creating a Git tag).

#### **Release Stage Logic**

The CLI's menu options will dynamically change based on the current version, adhering strictly to the rules you've defined.

* **If the current version is a Prototype (v0.x.x-next.x):**  
  * **Option 1: Increment Prototype.** Increase the PRERELEASE number (e.g., v0.1.0-next.1 becomes v0.1.0-next.2).  
  * **Option 2: Transition to Early Access.** Remove the prerelease suffix and set the patch to 0 (e.g., v0.1.0-next.1 becomes v0.1.0).  
* **If the current version is an Early Access Release (v0.x.x):**  
  * **Option 1: Increment Patch.** Increase the PATCH version (e.g., v0.2.5 becomes v0.2.6).+  
  * **Option 2: Increment Minor.** Increase the MINOR version and reset the PATCH to 0 (e.g., v0.2.5 becomes v0.3.0).  
  * **Option 3: Transition to Early Stable.** Change the MAJOR version to 1, and reset MINOR and PATCH to 0 (e.g., v0.9.9 becomes v1.0.0).  
* **If the current version is an Early Stable Release (v1.0.x):**  
  * **Option 1: Increment Patch.** Increase the PATCH version (e.g., v1.0.2 becomes v1.0.3).  
  * **Option 2: Transition to Stable.** Change the MINOR version to 1 (e.g., v1.0.3 becomes v1.1.0).  
* **If the current version is a Stable Release (v1.1.0 or higher):**  
  * **Option 1: Increment Patch.** Increase the PATCH version (e.g., v1.1.5 becomes v1.1.6).  
  * **Option 2: Increment Minor.** Increase the MINOR version and reset the PATCH to 0 (e.g., v1.1.5 becomes v1.2.0).
