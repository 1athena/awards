# GitHub platform setup

These are repository administration notes. These settings have **not** been applied by this repository initialization. The upstream repository is `TheJustinSunPrize/awards`; `Federico2014/awards` is the working fork. Changing repository settings, inviting owners, and enabling Pages are separate platform actions.

- Organization: `TheJustinSunPrize`; proposed display name: `The Justin Sun Prize`; repository: `awards`; default branch: `main`.
- Confirm at least two organization owners before recording awards. Use an organizational public email and the correct legal entity. Confirm public commit identity and a suitable GitHub noreply address before committing.
- Enable Issues and Discussions; enable other collaboration features as needed. Pin the [Discussions notice](discussions-notice.md) when Discussions is enabled.
- Protect `main`: require PRs and at least one approval, block force pushes and branch deletion, and apply the rules without administrator bypass. Remove required status checks for retired workflows from branch protection or rulesets.
- Configure Pages separately when a renderer exists. This initialization provides content and data but no website build or deployment. Confirm the actual Pages URL and custom domain in the upstream repository settings before publishing links.
- Keep payments outside the information site and repository. Store large artifacts externally with permanent IDs and checksums.

Configure public submission contacts and repository ownership separately. Code uses MIT and content/data use CC BY 4.0; third-party material retains its original license.
