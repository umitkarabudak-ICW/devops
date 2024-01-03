from redis.sentinel import Sentinel
import threading
import time

def write_and_verify_data(redis_client, user_id):
    key = f'user_{user_id}_key'
    value_to_store = f'user_{user_id}_value'

    # Veriyi Redis'e yaz
    redis_client.set(key, value_to_store)
    print(f"Kullanici {user_id}: Veri Redis'e başariyla eklendi. Anahtar: {key}, Değer: {value_to_store}")

    while True:
        # Veriyi Redis'den oku
        retrieved_value = redis_client.get(key)
        if retrieved_value:
            retrieved_value = retrieved_value.decode('utf-8')
            print(f"Kullanici {user_id}: Redis'ten alinan değer: {retrieved_value}")

            # Veriyi doğrula
            if retrieved_value == value_to_store:
                print(f"Kullanici {user_id}: Veri doğrulandi.")
            else:
                print(f"Kullanici {user_id}: Hata: Alinan veri, beklenen veri ile uyuşmuyor.")
        else:
            print(f"Kullanici {user_id}: Hata: Belirtilen anahtar Redis veritabaninda bulunamadi.")
        time.sleep(1)

def main():
    redis_host = 'api.rsm-prod-cloud.vodafone.local'
    redis_port = 6379
    redis_auth_pass = 'Redis1234'

    sentinel = Sentinel([('api.rsm-prod-cloud.vodafone.local', 6379)], socket_timeout=0.1)
    master = sentinel.master_for('mymaster', socket_timeout=0.1)
    #redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_auth_pass)

    user_count = 100
    threads = []

    # Her bir kullanicı için bir thread oluştur
    for user_id in range(user_count):
        thread = threading.Thread(target=write_and_verify_data, args=(master, user_id))
        threads.append(thread)

    # Thread'leri başlat
    for thread in threads:
        thread.start()

    # Thread'lerin tamamlanmasini bekle
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
