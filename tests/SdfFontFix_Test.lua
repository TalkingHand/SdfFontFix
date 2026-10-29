-- Test only (pzt TEST_FILES): open a print media window the way the debug menu does.
KoFontTest = KoFontTest or {}

function KoFontTest.openPrint(registry, index)
    if KoFontTest.win then
        UIManager.RemoveElement(KoFontTest.win.javaObj)
        KoFontTest.win = nil
    end
    local entry = registry ~= "NEWSPAPER" and Registries[registry]:values():get(index)
    local title, info
    if registry == "NEWSPAPER" then
        -- index is a title substring here: pick the first issue whose title key contains it
        for i = 0, Registries.NEWSPAPER:values():size() - 1 do
            local book = Registries.NEWSPAPER:values():get(i)
            for j = 0, book:getIssues():size() - 1 do
                local issue = book:getIssues():get(j)
                if not title and string.find(book:getTitle(issue), index, 1, true) then
                    title, info = book:getTitle(issue), book:getTranslationInfoKey(issue)
                end
            end
        end
        if not title then
            print("[SdfFontFix] no newspaper matching " .. tostring(index))
            return
        end
    else
        title, info = entry:getTranslationKey(), entry:getTranslationInfoKey()
    end
    local win = PZAPI.UI.PrintMedia{ x = 675, y = 10 }
    win.media_id = title
    win.data = getText(info)
    win.children.bar.children.name.text = getText(title)
    win.textTitle = getText(title)
    win.textData = string.gsub(getText(info), "\\n", "\n")
    win:instantiate()
    KoFontTest.win = win
    print("[SdfFontFix] opened " .. registry .. " " .. title)
end

-- the notebook button under the picture: shows the title (SdfOldBold) and text (SdfRegular) panel
function KoFontTest.showText()
    KoFontTest.win.children.bottomButtons.children.readNewspaper:onLeftClick()
    print("[SdfFontFix] text panel: " .. tostring(KoFontTest.win.textTitle))
end

-- vanilla translations have almost no print media text in KO (Print_Media 0 keys, Print_Text 3
-- titles), so put the Knox News title and a few UI strings into the panel to see the language's
-- script in SdfOldBold (title) and SdfRegular (text). Strings come from getText: the game does not
-- read non-ASCII in Lua sources as UTF-8.
function KoFontTest.koreanPanel()
    local win = KoFontTest.win
    local body = win.children.body.children.textNode.children.container
    local title = getText("Print_Text_KnoxKnews_July1_title")
    body.children.title:setText(title)
    body.children.text:setText(getText("IGUI_health_Good") .. " / " .. getText("Fluid_Unknown") .. "\n"
        .. getText("IGUI_Temperature") .. ": " .. getText("Sandbox_Normal") .. "\n"
        .. getText("Tooltip_FishingTip"))
    print("[SdfFontFix] print panel: " .. title)
end
