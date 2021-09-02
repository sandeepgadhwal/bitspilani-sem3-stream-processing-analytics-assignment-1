# bitspilani-sem3-stream-processing-analytics-assignment-1
bitspilani-sem3-stream-processing-analytics-assignment-1


# Build Docker Image
```bash
./docker/build_run_from_root.sh
```

## SSH into a new docker container from docker image
```bash
docker run --rm -it --privileged --entrypoint /bin/bash spa-asgm
```

## Start Kubernetes Service
```bash
kubectl create -f postService.yaml
```
