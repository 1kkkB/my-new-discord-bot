import discord
from discord.ext import commands
import sqlite3
from keep_alive import keep_alive 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Bot is online')

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_role(1056288414418341898)
async def ping(ctx):
    """Отправляет задержку между клиентом и сервером в миллисекундах"""
    await ctx.send(f' Задержка: {round(bot.latency * 1000)}ms')

@bot.command(name='test')
async def test(ctx):
  # отправка сообщения в лс участнику
  await ctx.author.send('Пока что вылглядит так.')

@bot.command(name='ответ')
async def test(ctx):
  # для Алекса
  await ctx.author.send('Ну знаешь, я не против с тобой подраться. Я и так знаю, что я сильнейший тут и ты меня не осилишь, так что иди прогуляйся во дворике и поиграй со свомии друзьями пока не поздно, ведь такими темпами ты не сможешь даже это делать)')

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def анкеты(ctx):
    allowed_roles = [
        1056288414418341898,
        1061866198880485437,
        1061704755484823562,
        1061943726102040586,
        1061943964065869844,
        1101019742074064959,
        1061942745888997406,
        1101019689511030784,
        1061883409288405002,
        1101029577675001927,
        1081272984637022209,
        1074744676655059014,
        1062466057736028260,
        1081280279974514769
    ]
    user_roles = [role.id for role in ctx.author.roles]
    if 991083583831678976 not in user_roles and not set(user_roles).intersection(allowed_roles):
        await ctx.send("Вам не дозволено использовать данную команду.")
        return

    embed = discord.Embed(title="Чтобы зарегистрироваться вам нужно создать тикет и написать заявку на Президента/ЧВК/Восстания.", color=discord.Color.dark_green())
    embed.set_footer(text="Вы можете сменить страну без сброса всего прогресса, один раз за вайп.")

    panel = """
**Для заявки на Президента**
```1. Ваша страна.
2. Флаг вашей страны.
3. Ваш онлайн в день.
4. Согласны ли вы с правилами нашего сервера?
5. Откуда вы узнали про наш ВПИ?```

**Для заявки на ЧВК**
```1. Название вашего ЧВК.
2. Символика вашего ЧВК.
3. Город в котором будет находиться основное здание вашего ЧВК.
4. Ваш онлайн в день.
5. Согласны ли вы с правилами нашего сервера?
6. Откуда вы узнали про наш ВПИ?```

**Для заявки Восстания**
```1. Название вашего Восстания.
2. Флаг вашего Восстания.
3. Цель вашего Восстания.
4. Причина вашего Восстания(Причина должна быть адекватной).
5. Ваш онлайн в день.
6. Согласны ли вы с правилами нашего сервера?
7. Откуда вы узнали про наш ВПИ?```
"""
    embed.add_field(name="", value=panel)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    # Ограничиваем количество сообщений до 99
    if amount > 999:
        amount = 999

    if amount <= 0:
        return await ctx.send("Вы должны ввести любое число от 1 до 999.")

    # Создаем вложенный эмбед для подтверждения
    confirm_embed = discord.Embed(
        title="Подтверждение очистки",
        description=f"Вы точно уверены, что хотите удалить {amount} сообщений?",
        color=discord.Color.orange()
    )

    # Отправляем эмбед с подтверждением и добавляем реакции
    confirm_message = await ctx.send(embed=confirm_embed)
    await confirm_message.add_reaction('✅')  # Кнопка подтверждения
    await confirm_message.add_reaction('❌')  # Кнопка отмены

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=259200.0, check=check)
    except asyncio.TimeoutError:
        await confirm_message.delete()
        return await ctx.send("🕛 Время истекло.")
    else:
        if str(reaction.emoji) == '✅':
            await confirm_message.delete()
            # Получаем список сообщений для удаления
            messages = []
            async for message in ctx.channel.history(limit=amount+1):
                messages.append(message)
            # Удаляем сообщения
            await ctx.channel.delete_messages(messages)

            # Создаем эмбед с информацией об удаленных сообщениях
            success_embed = discord.Embed(
                title="Очистка выполнена",
                description=f"✅ Удалено {len(messages)} сообщений(я).",
                color=discord.Color.green()
            )

            # Отправляем эмбед с информацией об удаленных сообщениях
            success_message = await ctx.send(embed=success_embed)
            await asyncio.sleep(3)
            await success_message.delete()
        else:
            await confirm_message.delete()
            cancel_embed = discord.Embed(
                title="❌ Действие отменено",
                color=discord.Color.red()
            )
            await ctx.send(embed=cancel_embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int, *, reason: str = None):
    # Проверяем, что у бота есть права для управления ролями
    if not ctx.guild.me.guild_permissions.manage_roles:
        return await ctx.send("❌ У меня нет прав для управления ролями.")

    # Получаем роль "Muted" или создаем ее, если она не существует
    muted_role = discord.utils.get(ctx.guild.roles, name="🙊 ◑ В Муте")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="🙊 ◑ В Муте")

        # Применяем права роли "Muted" на каналы сервера
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    # Замьючиваем участника
    await member.add_roles(muted_role, reason=reason)

    embed = discord.Embed(title="🙊 | Мьют", description=f"Участник {member.mention} был замьючен", color=discord.Color.red())
    embed.add_field(name="Модератор", value=ctx.author.mention, inline=True)
    embed.add_field(name="Продолжительность", value=f"{duration} минут(ы)")
    embed.add_field(name="Причина", value=reason or "Не указана")
    await ctx.send(embed=embed)

    # Ждем указанное время и размьючиваем участника
    await asyncio.sleep(duration * 60)
    await member.remove_roles(muted_role)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    # Проверяем, что у бота есть права для управления ролями
    if not ctx.guild.me.guild_permissions.manage_roles:
        return await ctx.send("У меня недостаточно прав для управления ролями.")

    # Получаем роль "Muted"
    muted_role = discord.utils.get(ctx.guild.roles, name="🙊 ◑ В Муте")
    if not muted_role:
        return await ctx.send("Роль '🙊 ◑ В Муте' не существует или участник не замьючен.")

    # Размьючиваем участника
    await member.remove_roles(muted_role)

    embed = discord.Embed(title="🙉 | Размьют", description=f"Участник {member.mention} был размьючен", color=discord.Color.green())
    await ctx.send(embed=embed)


@bot.command()
async def ban(ctx, member: discord.Member, duration: int, reason: str):
    if not ctx.author.guild_permissions.ban_members:
        return await ctx.send("❌ У вас не достаточно прав для использования данной команды.")

    embed = discord.Embed(title="🔒 | Участник Забанен", color=discord.Color.red())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Модератор", value=ctx.author.mention, inline=True)
    embed.add_field(name="Участник", value=member.mention, inline=False)
    embed.add_field(name="Длительность", value=f"{duration} minutes", inline=False)
    embed.add_field(name="Причина", value=reason, inline=False)

    await member.ban(reason=reason)

    ban_channel = discord.utils.get(ctx.guild.channels, name="ban-logs")
    if ban_channel:
        await ban_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        embed = discord.Embed(title="Ошибка", description="❌ Вы не можете кикнуть самого себя.", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    if member.top_role.position >= ctx.author.top_role.position:
        embed = discord.Embed(title="Ошибка", description=f"❌ Вы не можете кикнуть {member.mention}, потому что роль данного участника выше или равна вашей роли.", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    embed = discord.Embed(title=f"Кикнут {member.name}#{member.discriminator}", color=discord.Color.red())
    embed.add_field(name="Модератор", value=ctx.author.mention, inline=True)
    
    if reason:
        embed.add_field(name="Причина", value=reason, inline=True)
    
    try:
        await member.send(f"Вы были кикнуты с сервера {ctx.guild.name}. Причина: {reason}")
    except:
        pass
    
    await member.kick(reason=reason)
    
    await ctx.send(embed=embed)

import random

@bot.command()
async def кости(ctx):
    dice_1 = random.randint(1, 6)
    dice_2 = random.randint(1, 6)
    total = dice_1 + dice_2
    
    embed = discord.Embed(title="🎲 | Бросок костей", color=discord.Color.blue())
    embed.add_field(name="Первая кость", value=dice_1, inline=True)
    embed.add_field(name="Вторая кость", value=dice_2, inline=True)
    embed.add_field(name="Итоговая сумма", value=total, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='виселица')
async def hangman(ctx):
    words = [
        'apple', 'banana', 'orange', 'cherry', 'grape', 'watermelon', 'pineapple', 'pear', 'kiwi', 'mango',
        'strawberry', 'blueberry', 'lemon', 'peach', 'plum', 'apricot', 'coconut', 'fig', 'pomegranate', 'lime',
        'avocado', 'blackberry', 'cranberry', 'raspberry', 'guava', 'papaya', 'melon', 'lychee', 'passionfruit', 'date',
        'dragonfruit', 'durian', 'kiwifruit', 'starfruit', 'persimmon', 'quince', 'cantaloupe', 'jackfruit', 'rhubarb',
        'boysenberry', 'elderberry', 'gooseberry', 'huckleberry', 'mulberry', 'nectarine', 'tangerine', 'mandarin',
        'apartment', 'house', 'villa', 'cottage', 'mansion', 'bungalow', 'condo', 'castle', 'farmhouse', 'cabin',
        'school', 'university', 'library', 'museum', 'hospital', 'bank', 'restaurant', 'cafe', 'hotel', 'cinema',
        'car', 'bicycle', 'motorcycle', 'bus', 'train', 'airplane', 'ship', 'taxi', 'truck', 'helicopter',
        'dog', 'cat', 'rabbit', 'hamster', 'horse', 'bird', 'turtle', 'snake', 'fish', 'elephant',
        'book', 'pen', 'pencil', 'paper', 'notebook', 'computer', 'phone', 'keyboard', 'guitar', 'paintbrush',
        'music', 'art', 'sports', 'nature', 'travel', 'food', 'movies', 'books', 'science', 'history'
    ]

    word = random.choice(words)  # Случайное выбор слова
    attempts = 6  # Количество попыток
    
    # Создаем начальный эмбед с информацией о виселице
    embed = discord.Embed(title='Виселица', color=discord.Color.blue())
    embed.add_field(name='Слово', value=' '.join(['_' for _ in word]), inline=False)
    embed.add_field(name='Попытки', value=str(attempts), inline=False)
    message = await ctx.send(embed=embed)
    
    guessed_letters = []  # Список угаданных букв
    
    while attempts > 0:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        try:
            guess_msg = await bot.wait_for('message', check=check, timeout=60)  # Ожидаем сообщение с предполагаемой буквой
        except asyncio.TimeoutError:
            return await ctx.send('Время истекло. Игра окончена.')
        
        guess = guess_msg.content.lower()  # Предполагаемая буква в нижнем регистре
        
        if guess in guessed_letters:
            await ctx.send('Вы уже угадали эту букву.')
            continue
        
        guessed_letters.append(guess)
        
        if guess in word:
            # Обновляем эмбед, отображая угаданную букву в слове
            masked_word = ' '.join([letter if letter in guessed_letters else '_' for letter in word])
            embed.set_field_at(0, name='Слово', value=masked_word, inline=False)
            await message.edit(embed=embed)
            
            if '_' not in masked_word:
                # Создаем эмбед с сообщением о выигрыше
                win_embed = discord.Embed(title='Виселица - Победа', color=discord.Color.green())
                win_embed.add_field(name='Загаданное слово', value=word, inline=False)
                return await ctx.send(embed=win_embed)
        else:
            attempts -= 1
            embed.set_field_at(1, name='Попытки', value=str(attempts), inline=False)
            await message.edit(embed=embed)
            
            if attempts == 0:
                # Создаем эмбед с сообщением о проигрыше
                loss_embed = discord.Embed(title='Виселица - Поражение', color=discord.Color.red())
                loss_embed.add_field(name='Загаданное слово', value=word, inline=False)
                return await ctx.send(embed=loss_embed)
    
    await ctx.send('Игра окончена.')

keep_alive()
import os
my_secret = os.environ['TOKEN']
bot.run(my_secret)
