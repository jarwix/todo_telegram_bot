import aiomysql
import aiomysql.cursors
import config
from datetime import datetime
import asyncio


async def connection():
    conn = await aiomysql.connect(host=config.mysqlhost,
                                  user=config.mysqlusername,
                                  password=config.mysqlpassword,
                                  db=config.mysqldbname,
                                  port=config.mysqlport,
                                  charset='utf8mb4')
    return conn


async def add_new_task(id_tg, task, time=None):
    conn = await connection()
    async with conn.cursor() as cursor:
        if time is not None:
            time = datetime.strptime(time, '%H:%M %Y-%m-%d')
            time = time.replace(second=0, microsecond=0)
        sql = "INSERT INTO tasksdata (idtg, tasks, time) VALUES (%s, %s, %s)"
        await cursor.execute(sql, (id_tg, task, time))
        await conn.commit()
        await cursor.close()
    conn.close()
    return


async def take_all_tasks(id_tg):
    conn = await connection()
    async with conn.cursor() as cursor:
        sql = "SELECT * FROM tasksdata WHERE idtg=%s"
        await cursor.execute(sql, (str(id_tg)))
        line = cursor.fetchall()
        if line is not None:
            lines = await asyncio.gather(*[line])
        else:
            return_message = "Нет задач"
        await conn.commit()
        await cursor.close()
    conn.close()
    if line is not None:
        return lines
    else:
        return return_message


async def delete_task(id_user):
    conn = await connection()
    async with conn.cursor() as cursor:
        sql = "DELETE FROM tasksdata WHERE id=%s"
        await cursor.execute(sql, (str(id_user)))
        await conn.commit()
        await cursor.close()
    conn.close()
    return


async def check_datetime():
    conn = await connection()
    async with conn.cursor() as cursor:
        sql = "SELECT * FROM tasksdata WHERE TIME_TO_SEC(TIMEDIFF((NOW()), time)) >= 0 " \
              "AND TIME_TO_SEC(TIMEDIFF((NOW()),time)) < 60"
        await cursor.execute(sql)
        line = cursor.fetchall()
        if line is not None:
            lines = await asyncio.gather(*[line])
        else:
            return_message = "Нет задач"
        await conn.commit()
        await cursor.close()
    conn.close()
    if line is not None:
        return lines
    else:
        return return_message
