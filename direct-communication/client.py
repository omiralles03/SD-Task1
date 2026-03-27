import asyncio
import httpx
import time
import os

URL_BASE = "http://127.0.0.1:8000" 
MAX_CONCURRENTE = 100 

async def send_request(client, line, url_base, semaphore):
    async with semaphore:
        parts = line.strip().split()
        
        if not parts or parts[0].upper() != "BUY":
            return None

        # Tickets No Numerados
        if len(parts) == 3:
            _, c_id, r_id = parts
            params = {"client_id": c_id, "request_id": r_id}
            url = f"{url_base}/buy/unnumbered"
            
        # Tickets Numerados
        elif len(parts) == 4:
            try:
                _, c_id, s_id, r_id = parts
                params = {"client_id": c_id, "seat_id": int(s_id), "request_id": r_id}
                url = f"{url_base}/buy/numbered"
            except ValueError:
                # Si seat_id no es un número, ignorar
                return None
        else:
            return None

        try:
            # Enviamos la petición POST
            resp = await client.post(url, params=params)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

async def run_benchmark(filename):
    file_path = os.path.join("..", "benchmarks", filename)
    
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo en {os.path.abspath(file_path)}")
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENTE)

    async with httpx.AsyncClient(timeout=None) as client:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        print(f"Iniciando benchmark: {filename} ({len(lines)} líneas)...")
        start_time = time.perf_counter()
        
        # Crear las tareas para todas las líneas
        tasks = [send_request(client, line, URL_BASE, semaphore) for line in lines]
        
        # Ejecutartodo y filtramos las líneas ignoradas
        all_results = await asyncio.gather(*tasks)
        results = [r for r in all_results if r is not None]
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Cálculo de métricas
        success = sum(1 for r in results if r.get("status") == "success")
        rejected = sum(1 for r in results if r.get("status") == "rejected")
        errors = sum(1 for r in results if r.get("status") == "error")

        print("\n" + "="*40)
        print(f"RESULTADOS PARA: {filename}")
        print("-" * 40)
        print(f"Tiempo total:      {total_time:.2f} s")
        print(f"Throughput:        {len(results)/total_time:.2f} ops/s")
        print(f"Operaciones éxito: {success}")
        print(f"Operaciones rechazo: {rejected}")
        print(f"Errores de red:    {errors}")
        print("="*40 + "\n")

if __name__ == "__main__":
    archivo_test = "benchmark_unnumbered_20000.txt"
    asyncio.run(run_benchmark(archivo_test))