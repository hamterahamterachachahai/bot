# Discord Bot Project

## Overview

This is a Discord bot built with Python using the discord.py library. The bot features a modular architecture with multiple cogs providing various functionalities including administration, moderation, games, utilities, and fun commands. It supports both traditional prefix commands and Discord's slash commands through hybrid command implementation.

## System Architecture

### Core Architecture
- **Language**: Python 3.x
- **Framework**: discord.py with commands extension
- **Architecture Pattern**: Modular cog-based system
- **Command System**: Hybrid commands (supports both prefix and slash commands)
- **Configuration**: Environment variable-based configuration using .env files

### Bot Structure
The bot follows a cog-based modular architecture where each functionality group is separated into individual cogs:
- `bot.py` - Main bot file with core initialization and configuration
- `cogs/` directory containing feature modules

## Key Components

### Core Bot (`bot.py`)
- **Discord Intents**: Configured with members and message content intents
- **Logging System**: File and console logging with configurable levels
- **Permission System**: User ID and role-based access control
- **DM Functionality**: Built-in direct messaging capabilities with rate limiting

### Cog Modules

#### Administration (`cogs/admin.py`)
- **Purpose**: Bot administration and cog management
- **Access Control**: Owner-only and role-based permissions
- **Features**: Dynamic cog loading/unloading

#### Moderation (`cogs/moderation.py`)
- **Purpose**: Server moderation tools
- **Permissions**: Requires kick/ban/manage_messages permissions
- **Features**: Member kicking, with safety checks and logging

#### Games (`cogs/games.py`)
- **Purpose**: Interactive gaming commands
- **Features**: Rock Paper Scissors with emoji support

#### Fun (`cogs/fun.py`)
- **Purpose**: Entertainment commands
- **Features**: Dice rolling, coin flipping, magic 8-ball

#### General (`cogs/general.py`)
- **Purpose**: Basic server and user information
- **Features**: Server info, user info, ping commands

#### Information (`cogs/info.py`)
- **Purpose**: Bot statistics and system information
- **Features**: Bot performance metrics, system details

#### Utility (`cogs/utility.py`)
- **Purpose**: Utility tools for Discord
- **Features**: Discord timestamp conversion

#### Miscellaneous (`cogs/misc.py`)
- **Purpose**: Additional utility features
- **Features**: Reminder system with time parsing

## Data Flow

1. **Command Reception**: Bot receives commands through Discord API
2. **Permission Validation**: Checks user permissions and allowed lists
3. **Command Processing**: Routes commands to appropriate cogs
4. **Response Generation**: Creates embeds and formatted responses
5. **Logging**: Records actions and errors to files and console

## External Dependencies

### Required Libraries
- `discord.py` - Discord API wrapper
- `python-dotenv` - Environment variable management
- `psutil` - System performance monitoring
- `asyncio` - Asynchronous programming support

### Discord API Integration
- **Bot Token Authentication**: Secure token-based authentication
- **Permissions**: Granular permission system with role and user ID checking
- **Intents**: Members and message content intents for full functionality

## Deployment Strategy

### Environment Configuration
The bot uses environment variables for configuration:
- `DISCORD_BOT_TOKEN` - Bot authentication token
- `ALLOWED_USER_IDS` - Comma-separated list of authorized user IDs
- `ALLOWED_ROLE_IDS` - Comma-separated list of authorized role IDs
- `DM_DELAY` - Rate limiting for direct messages
- `LOG_DMS` - Boolean flag for DM logging

### Logging Strategy
- **File Logging**: Persistent logs stored in `bot.log`
- **Console Logging**: Real-time output for monitoring
- **Log Levels**: Configurable logging levels with INFO default

### Error Handling
- **Graceful Degradation**: Commands fail safely with user feedback
- **Permission Errors**: Clear messaging for insufficient permissions
- **Rate Limiting**: Built-in cooldowns to prevent spam

## Changelog

```
Changelog:
- July 06, 2025. Initial setup with hybrid commands and user restrictions
- July 06, 2025. Moved all configuration to .env file for flexibility
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
Bot access restrictions: Only specific user IDs can use the bot - 1371770747692777553, 1318613193215705211, 1151217188951298138, 980130432882454578
```