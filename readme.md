# Docker Job Service

## Approach

I focused on keeping the implementation modular without introducing unnecessary complexity. I separated the API and scanner into independent services, used background processing to avoid blocking requests, and Docker Compose to simplify deployment.

One of my main design decisions was to prioritize Dockerfile security scanning before building the image. Building an image already consumes resources and can introduce security risks, as Dockerfile instructions can execute arbitrary commands during the build process. Early scanning helps reject potentially unsafe Dockerfiles before those risks are introduced.

I also included post-build vulnerability scanning, resource restrictions, and automatic cleanup of temporary Docker resources.

## Running the Project

Configure `.env`, then run:

`docker compose up --build -d`

```
curl -X POST http://localhost:8001/jobs   -H "Content-Type: text/plain"   --data-binary @examples/valid.Dockerfile
curl http://localhost:8001/jobs/{job_id}
```

API documentation is available at `http://localhost:8001/docs`.

## Limitations and Future Improvements

Given more time, there are several things I would like to improve or explore:

Consider using an internal package registry with pre-approved dependencies to have more control over what gets installed during builds.

Currently, only the Dockerfile is included in the build context. I would extend this to support additional files referenced through COPY or ADD.

Look into supporting more complex build workflows, particularly those that produce multiple images. Multi-stage Dockerfiles already work, but the service only tracks one final image.

Improve the image scanning process to catch more vulnerabilities, particularly those introduced through additional packages and dependencies during the build.

Add further restrictions to containers and improve isolation. While some limits are already in place, there is more that could be done, especially around Docker Engine access and build security.

Add more unit and integration tests to verify each component independently, as well as the full workflow.

Explore how performance could be measured more meaningfully. Currently, the service simply retrieves the value reported by the container, but what constitutes performance would depend on the workload being submitted.

Move away from in-memory job storage and introduce a database and proper job queue to handle more jobs reliably.

Use Terraform to define the infrastructure and make it easier to deploy the application across different environments.

Build a small Python wrapper around the API to make submitting Dockerfiles and checking job statuses easier.

Add authentication and authorization so users can securely submit jobs and access their previous results.

Create a simple interface where users can track their jobs, alongside an admin dashboard to monitor ongoing jobs, failures, and resource usage.