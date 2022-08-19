# Environment

All development and testing has been done in Linux. These scripts should work as expected on MacOS and WSL but this has not been confirmed and I cannot test this.

## Requirements

- Docker
- docker-compose

Additionally a venv to install `requirements.test.txt`

## Running

`./scripts/run-master`

This script will:

- Build the `base` container image (`docker/Docker.base`)
- Build the `master` container image (`docker/Docker.master`)
- Remove any old docker-compose containers
- Start `master` container and `dynamodb-local` container.

Documenation for [dynamodb-local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)

## Testing

All testing is done within containers, with the `test` container (`docker/Docker.test`) being the main container used for all testing.
Because of this it's built on top of the `cdk` container (`docker/Docker.cdk`).

Note that none of the test scripts will build the `test` container by default. This is to avoid building it everytime tests are run and help speed up development.

To build the `test` container run `./scripts/build-test`

### Unit Testing

`./scripts/run-test-unit`

This script will:

- Run tests within `test/unit/master` and `test/unit/storage`

### CDK Unit Testing

`./scripts/run-test-cdk`

This script will:

- Run tests within `test/unit/cdk`

These are split out into their own test suite as they're fairly independant of the main application code.

## Linting

To enforce some level of code consistency and quality there are a lot of linting scripts. See `./scripts/ci` for the complete list.

If you're unsure of which linting script to run use `./scripts/lint-all`.

If you're writing code you probably want `./scripts/lint-python`. Use the individual scripts in `./scripts/ci` when troubleshooting/resolving specific linting errors.

Otherwise for documentation changes there's `./scripts/ci/lint-docs` to check and `./scripts/docs/lint-and-fix-docs` to fix any linting issues.
