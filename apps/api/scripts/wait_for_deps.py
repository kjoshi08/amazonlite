import os
import socket
import time


def wait_for_host(host: str, port: int, name: str, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    last_err = None

    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"[wait] {name} ready at {host}:{port}")
                return
        except OSError as e:
            last_err = e
            time.sleep(1)

    raise RuntimeError(
        f"[wait] Timed out waiting for {name} at {host}:{port}. Last error: {last_err}"
    )


if __name__ == "__main__":
    # ✅ Compose service name is "postgres", not "db"
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))

    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    wait_for_host(db_host, db_port, "postgres", timeout_s=90)
    wait_for_host(redis_host, redis_port, "redis", timeout_s=90)
