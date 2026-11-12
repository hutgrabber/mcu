# One image for every local tool: Playwright with its browsers, Java for the Firebase emulator,
# and Python with Pillow and Playwright for scripts/assets.py.
FROM mcr.microsoft.com/playwright:v1.64.1-noble
RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-21-jre-headless python3-pip python3-pil \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir --break-system-packages playwright==1.64.1
WORKDIR /app
COPY tests/docker-entry.sh /usr/local/bin/docker-entry
ENTRYPOINT ["docker-entry"]
CMD ["bash"]
