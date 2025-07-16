import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Bot Configuration
BOT_TOKEN = "7725943119:AAHMsCJVfH-Sl_U-pNu4U3VjFplV0YgU4Xs"
TWITTER_URL = "https://twitter.com/mykelajibade"
TELEGRAM_CHANNEL = "t.me/mykelajibade"
TELEGRAM_GROUP = "https://t.me/mykelajiabde"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# SOL address validation
def validate_sol_address(address: str) -> bool:
    return bool(re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", address))

# Initialize user data
def init_user_data(context: ContextTypes.DEFAULT_TYPE):
    if 'tasks' not in context.user_data:
        context.user_data['tasks'] = {
            'twitter': False,
            'facebook': False,
            'wallet_submitted': False
        }

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_user_data(context)
    user = update.effective_user
    welcome_msg = (
        "🔰 *Welcome to BLVQSpace Airdrop!*\n\n"
        "📋 *Complete these simple tasks:*\n"
        f"1. Join our [Telegram Channel]({TELEGRAM_CHANNEL})\n"
        f"2. Join our [Telegram Group]({TELEGRAM_GROUP})\n"
        f"3. Follow our [Twitter]({TWITTER_URL})\n"
        "4. Follow our Facebook (link coming soon)\n"
        "5. Submit your SOL wallet address\n\n"
        "_This is a test bot. No real SOL will be distributed._"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Verify Tasks", callback_data="verify_tasks")]
    ]
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# Verify tasks handler
async def verify_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    init_user_data(context)
    
    tasks = context.user_data['tasks']
    status_msg = (
        "📊 *Your Task Status:*\n\n"
        f"1. Telegram Channel: ✅ (Auto-verified)\n"
        f"2. Telegram Group: ✅ (Auto-verified)\n"
        f"3. Twitter Followed: {'✅' if tasks['twitter'] else '❌'}\n"
        f"4. Facebook Followed: {'✅' if tasks['facebook'] else '❌'}\n"
        f"5. SOL Wallet Submitted: {'✅' if tasks['wallet_submitted'] else '❌'}\n\n"
        "_Click the buttons below to complete tasks_"
    )
    
    keyboard = []
    if not tasks['twitter']:
        keyboard.append([InlineKeyboardButton("🐦 Verify Twitter", callback_data="verify_twitter")])
    if not tasks['facebook']:
        keyboard.append([InlineKeyboardButton("👍 Verify Facebook", callback_data="verify_facebook")])
    if not tasks['wallet_submitted']:
        keyboard.append([InlineKeyboardButton("💰 Submit SOL Wallet", callback_data="submit_wallet")])
    keyboard.append([InlineKeyboardButton("🔄 Refresh Status", callback_data="verify_tasks")])
    
    await query.edit_message_text(
        status_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Button handlers
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "verify_tasks":
        await verify_tasks(update, context)
    elif data == "verify_twitter":
        await verify_twitter(update, context)
    elif data == "verify_facebook":
        await verify_facebook(update, context)
    elif data == "submit_wallet":
        await submit_wallet(update, context)

# Twitter verification handler
async def verify_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['tasks']['twitter'] = True
    
    msg = (
        "🐦 *Twitter Follow Verified!*\n\n"
        f"Thank you for following [our Twitter]({TWITTER_URL}).\n"
        "You can now continue with other tasks."
    )
    
    await query.edit_message_text(
        msg,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await verify_tasks(update, context)

# Facebook verification handler
async def verify_facebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['tasks']['facebook'] = True
    
    msg = (
        "👍 *Facebook Follow Verified!*\n\n"
        "Thank you for following our Facebook page.\n"
        "You can now continue with other tasks."
    )
    
    await query.edit_message_text(
        msg,
        parse_mode="Markdown"
    )
    await verify_tasks(update, context)

# Wallet submission handler
async def submit_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text("💳 *Please send your SOL wallet address:*", parse_mode="Markdown")

# Handle wallet input
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_address = update.message.text.strip()
    
    if validate_sol_address(wallet_address):
        context.user_data['tasks']['wallet_submitted'] = True
        tasks = context.user_data['tasks']
        
        if tasks['twitter'] and tasks['facebook']:
            congrats_msg = (
                "🎉 *CONGRATULATIONS!*\n\n"
                "You've successfully completed all tasks for the BLVQSpace Airdrop!\n\n"
                "100 SOL has been sent to your wallet:\n"
                f"`{wallet_address}`\n\n"
                "Well done! Hope you didn't cheat the system 😉\n\n"
                "_Note: This is a test bot. No real SOL has been sent._"
            )
            await update.message.reply_text(
                congrats_msg,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "✅ *Wallet saved!*\n\n"
                "Please complete the remaining tasks to qualify for the airdrop.",
                parse_mode="Markdown"
            )
            await verify_tasks(update, context)
    else:
        await update.message.reply_text(
            "⚠️ *Invalid SOL address!*\n\n"
            "Please send a valid SOL wallet address:",
            parse_mode="Markdown"
        )

# Main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
