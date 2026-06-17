return {
  {
    "arcticicestudio/nord-vim",
    init = function()
      vim.api.nvim_create_autocmd("ColorScheme", {
        pattern = "nord",
        callback = function()
          for _, group in ipairs({
            "Normal",
            "NormalNC",
            "SignColumn",
            "LineNr",
            "FoldColumn",
            "EndOfBuffer",
            "NormalFloat",
            "FloatBorder",
          }) do
            vim.api.nvim_set_hl(0, group, { bg = "none" })
          end
        end,
      })
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "nord",
    },
  },
}
