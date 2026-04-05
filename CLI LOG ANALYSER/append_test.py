from datetime import datetime

ts = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0530")

with open("sample_logs/watch_test.log", "a", encoding="utf-8") as f:
    f.write(f'192.168.1.1 - - [{ts}] "GET /api/users HTTP/1.1" 500 100 "-" "curl/7.68.0"\n')
    f.write(f'192.168.1.1 - - [{ts}] "GET /api/users HTTP/1.1" 500 100 "-" "curl/7.68.0"\n')
    f.write(f'192.168.1.1 - - [{ts}] "GET /api/users HTTP/1.1" 500 100 "-" "curl/7.68.0"\n')
print("done")