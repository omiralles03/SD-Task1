import asyncio
import httpx
import time
import os
import sys

URL_BASE = "http://127.0.0.1:80" 
MAX_CONCURRENTE = 100 

async def send_request(client, line, url_base, semaphore):
    async with semaphore: 
        parts = line.strip().split()
        
        if not parts or parts[0].upper() != "BUY":
            return None

        if len(parts) == 3:
            _, c_id, r_id = parts
            params = {"client_id": c_id, "request_id": r_id}
            url = f"{url_base}/buy/unnumbered"
        elif len(parts) == 4:
            try:
                _, c_id, s_id, r_id = parts
                params = {"client_id": c_id, "seat_id": int(s_id), "request_id": r_id}
                url = f"{url_base}/buy/numbered"
            except ValueError:
                return None
        else:
            return None

        try:
            resp = await client.post(url, params=params)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

async def run_benchmark(file_path):
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo en {os.path.abspath(file_path)}")
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENTE)
    metrics = {"success": 0, "rejected": 0, "error": 0, "total": 0}

    async with httpx.AsyncClient(timeout=None) as client:
        print(f"Iniciando benchmark: {file_path}...")
        start_time = time.perf_counter()
        
        tasks = set()
        
        with open(file_path, 'r') as f:
            for line in f:
                if len(tasks) >= MAX_CONCURRENTE:
                    done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                    for t in done:
                        process_result(t.result(), metrics)

                new_task = asyncio.create_task(send_request(client, line, URL_BASE, semaphore))
                tasks.add(new_task)

        if tasks:
            done, _ = await asyncio.wait(tasks)
            for t in done:
                process_result(t.result(), metrics)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        print_statistics(file_path, total_time, metrics)

def process_result(result, metrics):
    if result is None:
        return
    
    metrics["total"] += 1
    status = result.get("status")
    if status == "success":
        metrics["success"] += 1
    elif status == "rejected":
        metrics["rejected"] += 1
    else:
        metrics["error"] += 1

def print_statistics(filename, total_time, metrics):
    print("\n" + "="*40)
    print(f"RESULTADOS PARA: {filename}")
    print("-" * 40)
    print(f"Tiempo total:      {total_time:.2f} s")
    print(f"Throughput:        {metrics['total']/total_time:.2f} ops/s")
    print(f"Operaciones éxito: {metrics['success']}")
    print(f"Operaciones rechazo: {metrics['rejected']}")
    print(f"Errores de red:    {metrics['error']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 client.py <benchmark>")
        sys.exit(1)

    path_argumento = sys.argv[1]
    asyncio.run(run_benchmark(path_argumento))
