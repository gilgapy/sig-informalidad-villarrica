-- Filtro pandoc para el informe FCE-UNVES (APA 7.ª ed.)
-- 1. Tablas a ancho automático (evita columnas comprimidas).
-- 2. Rótulos "Tabla N" / "Figura N", sus títulos y las notas sin sangría.
-- 3. Referencias con sangría francesa.

local LABEL_STYLE = "APA Rotulo"
local TITLE_STYLE = "APA Titulo"
local NOTE_STYLE = "APA Nota"
local REFERENCE_STYLE = "APA Referencia"

local function styled(style, block)
  return pandoc.Div({ block }, pandoc.Attr("", {}, { ["custom-style"] = style }))
end

local function starts_with_label(para)
  local first = para.content[1]
  if not first or first.t ~= "Strong" then return false end
  local text = pandoc.utils.stringify(first)
  return text:match("^Tabla %d+$") or text:match("^Figura %d+$")
end

local function is_note(para)
  local first = para.content[1]
  return first and first.t == "Emph" and pandoc.utils.stringify(first) == "Nota."
end

local function is_title(para)
  return #para.content == 1 and para.content[1].t == "Emph"
end

function Table(tbl)
  for i, spec in ipairs(tbl.colspecs) do
    tbl.colspecs[i] = { spec[1], pandoc.ColWidthDefault }
  end
  return tbl
end

function Blocks(blocks)
  local out = {}
  local expect_title = false
  local in_references = false
  for _, block in ipairs(blocks) do
    if block.t == "Header" and block.level == 1 then
      in_references = pandoc.utils.stringify(block):upper() == "REFERENCIAS"
    end
    if in_references and block.t == "Para" then
      table.insert(out, styled(REFERENCE_STYLE, block))
    elseif block.t == "Para" and starts_with_label(block) then
      table.insert(out, styled(LABEL_STYLE, block))
      expect_title = true
    elseif block.t == "Para" and expect_title and is_title(block) then
      table.insert(out, styled(TITLE_STYLE, block))
      expect_title = false
    elseif block.t == "Para" and is_note(block) then
      table.insert(out, styled(NOTE_STYLE, block))
      expect_title = false
    else
      table.insert(out, block)
      expect_title = false
    end
  end
  return out
end
