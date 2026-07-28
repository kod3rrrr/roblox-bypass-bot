#!/usr/bin/env python3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from playwright.async_api import async_playwright
import time
import os

BOT_TOKEN = "8612053860:AAF1ay4xnFA4fKuAKlN0pAl_WzhQu_FPuoU"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def bypass_cookie(cookie):
    """Автобайпасс через rblxbypasser.xyz"""
    async with async_playwright() as p:
        try:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto("https://rblxbypasser.xyz/b/Emailremover", timeout=30000)
            
            # Ждём загрузки страницы
            await page.wait_for_timeout(3000)
            
            # Ищем поле для куки
            cookie_input = await page.wait_for_selector("input[type='text']", timeout=15000)
            await cookie_input.fill(cookie)
            
            # Ищем кнопку submit
            submit_btn = await page.wait_for_selector("button[type='submit'], button:has-text('Submit'), button:has-text('Bypass'), button:has-text('Remove')", timeout=10000)
            await submit_btn.click()
            
            # Ждём результата
            await page.wait_for_timeout(12000)
            
            # Проверяем результат
            page_text = await page.content()
            page_text_lower = page_text.lower()
            
            await browser.close()
            
            if "success" in page_text_lower or "removed" in page_text_lower or "bypass" in page_text_lower:
                return True, "✅ Email успешно удалён"
            elif "invalid" in page_text_lower or "error" in page_text_lower or "failed" in page_text_lower:
                return False, "❌ Невалидная кука"
            else:
                return False, "⚠️ Неизвестный результат"
            
        except Exception as e:
            try:
                await browser.close()
            except:
                pass
            return False, f"❌ Ошибка: {str(e)[:150]}"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 **Roblox Email Bypass Bot**\n\n"
        "📤 Отправьте файл с куками (.txt)\n"
        "📝 Каждая кука на новой строке\n\n"
        "🔄 Автоматическая обработка через rblxbypasser.xyz\n\n"
        "Или отправьте одну куку текстом",
        parse_mode="Markdown"
    )

@dp.message(F.document)
async def handle_file(message: Message):
    """Обработка файла с куками"""
    
    if not message.document.file_name.endswith('.txt'):
        await message.answer("❌ Отправьте текстовый файл (.txt)")
        return
    
    # Скачиваем файл
    file = await bot.get_file(message.document.file_id)
    file_path = f"cookies_{message.from_user.id}_{int(time.time())}.txt"
    await bot.download_file(file.file_path, file_path)
    
    # Читаем куки
    with open(file_path, 'r', encoding='utf-8') as f:
        cookies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    os.remove(file_path)
    
    if not cookies:
        await message.answer("❌ Файл пустой или некорректный")
        return
    
    total = len(cookies)
    await message.answer(f"📋 Найдено кук: **{total}**\n\n⏳ Начинаю обработку...", parse_mode="Markdown")
    
    results = []
    
    for i, cookie in enumerate(cookies, 1):
        status_msg = await message.answer(f"🔄 Обработка **{i}/{total}**...", parse_mode="Markdown")
        
        # Обрабатываем куку
        success, result = await bypass_cookie(cookie)
        
        cookie_short = cookie[:40] + "..." if len(cookie) > 40 else cookie
        
        results.append({
            "success": success,
            "result": result,
            "cookie": cookie_short
        })
        
        await status_msg.edit_text(
            f"{result}\n\n`{cookie_short}`",
            parse_mode="Markdown"
        )
        
        # Задержка между запросами
        await asyncio.sleep(3)
    
    # Итоговый отчёт
    success_count = sum(1 for r in results if r['success'])
    failed_count = total - success_count
    
    report = (
        f"📊 **ИТОГОВЫЙ ОТЧЁТ**\n\n"
        f"✅ Успешно: **{success_count}**\n"
        f"❌ Ошибок: **{failed_count}**\n"
        f"📋 Всего: **{total}**\n\n"
    )
    
    if failed_count > 0:
        report += "**Детали ошибок:**\n"
        for i, r in enumerate(results, 1):
            if not r['success']:
                report += f"{i}. {r['result']}\n"
    
    await message.answer(report, parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: Message):
    """Обработка одной куки текстом"""
    
    cookie = message.text.strip()
    
    # Проверка минимальной длины куки
    if len(cookie) < 50:
        await message.answer(
            "❌ Это не похоже на куку\n\n"
            "Отправьте файл с куками или используйте /start"
        )
        return
    
    msg = await message.answer("🔄 Обработка...")
    
    success, result = await bypass_cookie(cookie)
    
    cookie_short = cookie[:40] + "..." if len(cookie) > 40 else cookie
    
    await msg.edit_text(
        f"{result}\n\n`{cookie_short}`",
        parse_mode="Markdown"
    )

async def main():
    print("=" * 50)
    print("Roblox Email Bypass Bot")
    print("Playwright + Firefox")
    print("=" * 50)
    print("Bot started successfully")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())