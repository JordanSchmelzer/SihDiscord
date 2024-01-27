# 💤🎵 Simplicity Music 🎵💤

Simplicity is an asynchronous music bot built off discord.py 2.0

## ✨ Features ✨

- Music queues
- Play, pause, skip, resume, volume, queue info among other commands
- custom command prefix support


```lua
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)
```
