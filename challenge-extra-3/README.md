# Challenge Extra 3: Helm Chart Tests
> HINT: Many more tests could be run and defined towards the high security and data privacy use cases of Orcrist and their customers. The following is a preview of `helm unittest` and that it works. Read more in my decisions taken headline.


I completed this task using [helm-unittest](https://github.com/helm-unittest/helm-unittest) for the chart in `challenge-5/server-chart`.
I implemented tests that verify the Deployment and Service render correctly with expected values.

## Installation Steps
I ensure the `helm-unittest` plugin is installed.

**Validate environment and install unittest.**
terminal> 
```bash
minikube start && minikube status
helm plugin install https://github.com/helm-unittest/helm-unittest.git --verify=false
```

## Decisions Taken For The Tests

I decided to write only two focused suites: one for Deployment and one for Service.
I chose this to keep the tests stable and aligned with Helm best practices, where I validate chart behavior (value wiring) instead of internal implementation details.

I expected and validated these parameters from `values.yaml` because they are actively used by the templates:

- Deployment expectations:
	- `replicaCount` -> `spec.replicas`
	- `image.repository` + `image.tag` -> container image
	- `image.pullPolicy` -> `imagePullPolicy`
- Service expectations:
	- `service.type` -> `spec.type`
	- `service.port` -> `spec.ports[0].port`
	- service routing contract -> `spec.ports[0].targetPort: http`

I also decided to test both default values and overrides, because this is the core Helm contract users rely on when installing charts with custom values.
I intentionally did not add assertions for helper-generated names/labels in this lean version, since those checks can become noisy and are less critical than runtime value wiring.

### Architectural Decision And ADR Mindset

I follow an architecture-first approach: I define the big picture and target mode of operations first, and then I deduce the concrete solution components from it.
For this challenge, the architectural decision is to package the app as a Helm chart because it supports easy scaling, simple maintenance, rapid development cycles, and clean integration into CI/CD pipelines through infrastructure-as-code.

I treat this as an Architecture Decision Record (ADR)-style choice:

- Context: I need repeatable, testable Kubernetes deployments for an application.
- Decision: I use Helm templating and helm-unittest to codify deployment behavior.
- Consequences: I gain consistent releases, safer changes, and faster feedback in automation.

I am genuinely passionate about this way of working, where architecture decisions are explicit, versioned in code, and continuously validated by automated tests.


## How-to Obtain The Result
1. I run tests for `challenge-5/server-chart`.
1. I confirm all suites pass.

I added assertions in the following test files:
- `challenge-5/server-chart/tests/deployment_test.yaml`
- `challenge-5/server-chart/tests/service_test.yaml`


## Run chart unit tests
terminal>
```bash
cd challenge-5
helm unittest ./server-chart
```


## How A Failed Test Run Can Look

If I introduce a wrong expected value in a test (for example, expecting `spec.ports[0].port` to be `9090` while default is `8080`), the output can look like this:

```bash
### Chart [ server-chart ] ./server-chart

 PASS  deployment values wiring server-chart/tests/deployment_test.yaml
 FAIL  service values wiring    server-chart/tests/service_test.yaml
 
	- service values wiring
		- uses default service values
			Error:
				template "service.yaml" assertion failed
				path: spec.ports[0].port
				expected: 9090
				actual:   8080

Charts:      0 passed, 1 failed, 1 total
Test Suites: 1 passed, 1 failed, 2 total
Tests:       3 passed, 1 failed, 4 total
```

I use this output to quickly identify which suite and assertion failed, then I fix either the expected value in the test or the chart value wiring in the template.


## A Short Explanation
I wrote a lean helm-unittest suite for Deployment and Service and validated both default values and override behavior.
All test design decisions and expected parameter mappings are documented in the section **Decisions Taken For The Tests** above.

