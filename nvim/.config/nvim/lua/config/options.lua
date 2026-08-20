vim.opt.termguicolors = true
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.expandtab = true
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2
vim.opt.smartindent = true
vim.opt.wrap = true
vim.opt.mouse = "a"
vim.opt.clipboard = "unnamedplus"
vim.opt.autoread = true

-- Folding: use Tree-sitter based expr folding, start files fully unfolded,
-- but keep a default foldlevel available via the command palette (<leader>p).
vim.opt.foldmethod = "expr"
vim.opt.foldexpr = "nvim_treesitter#foldexpr()"
vim.opt.foldlevel = 99
vim.opt.foldlevelstart = 99
vim.opt.foldenable = true

local reload_group = vim.api.nvim_create_augroup("ReloadChangedBuffers", { clear = true })
vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter", "CursorHold", "CursorHoldI", "TermClose" }, {
  group = reload_group,
  callback = function()
    if vim.bo.buftype == "" then
      vim.cmd("checktime")
    end
  end,
})
