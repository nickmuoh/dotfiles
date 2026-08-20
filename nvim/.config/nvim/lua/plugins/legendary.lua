return {
  {
    "stevearc/dressing.nvim",
    opts = {
      select = {
        backend = { "telescope" },
      },
    },
  },
  {
    "mrjones2014/legendary.nvim",
    priority = 10000,
    lazy = false,
    dependencies = {
      "nvim-telescope/telescope.nvim",
      "stevearc/dressing.nvim",
      "kkharji/sqlite.lua",
    },
    opts = {
      extensions = {
        lazy_nvim = true,
      },
      sort = {
        frecency = {
          db_root = vim.fn.stdpath("data"),
          max_timestamps = 10,
        },
      },
      commands = {
        { ":Format", description = "Format current buffer" },
        { ":Lazy", description = "Open Lazy plugin manager" },
        { ":Mason", description = "Open Mason LSP installer" },
        { ":RenderMarkdown buf_enable", description = "Render the current Markdown buffer" },
        { ":RenderMarkdown buf_disable", description = "Use the raw current Markdown buffer" },
        { ":set wrap!", description = "Toggle word wrap" },
        { "zM", description = "Fold: close all folds" },
        { "zR", description = "Fold: open all folds" },
        { "za", description = "Fold: toggle fold under cursor" },
        { "zc", description = "Fold: close fold under cursor" },
        { "zo", description = "Fold: open fold under cursor" },
        { ":set foldlevel=0", description = "Fold level: 0 (all closed)" },
        { ":set foldlevel=1", description = "Fold level: 1" },
        { ":set foldlevel=2", description = "Fold level: 2" },
        { ":set foldlevel=3", description = "Fold level: 3" },
        { ":set foldlevel=99", description = "Fold level: 99 (all open)" },
        { ":set foldmethod=indent", description = "Fold method: indent" },
        { ":set foldmethod=expr", description = "Fold method: expr (Tree-sitter)" },
        { ":set foldmethod=manual", description = "Fold method: manual" },
        { "u", description = "Undo" },
        { "<C-r>", description = "Redo" },
      },
      keymaps = {
        {
          "<leader>p",
          ":Legendary<CR>",
          description = "Open command palette",
          mode = { "n", "i", "v" },
        },
        {
          "<C-s>",
          ":w<CR>",
          description = "Save file",
          mode = { "n", "i", "v" },
        },
        {
          "<C-z>",
          "u",
          description = "Undo",
          mode = { "n" },
        },
        {
          "<C-z>",
          "<Esc>u",
          description = "Undo",
          mode = { "i" },
        },
        {
          "<C-z>",
          "<Esc>u",
          description = "Undo",
          mode = { "v" },
        },
      },
    },
  },
}
