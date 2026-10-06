// This single-node teaching image runs its pipeline on the built-in Jenkins node.
jenkins.model.Jenkins.get().setNumExecutors(1)
