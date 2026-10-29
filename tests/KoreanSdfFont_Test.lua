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
            print("[KoreanSdfFont] no newspaper matching " .. tostring(index))
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
    print("[KoreanSdfFont] opened " .. registry .. " " .. title)
end

-- the notebook button under the picture: shows the title (SdfOldBold) and text (SdfRegular) panel
function KoFontTest.showText()
    KoFontTest.win.children.bottomButtons.children.readNewspaper:onLeftClick()
    print("[KoreanSdfFont] text panel: " .. tostring(KoFontTest.win.textTitle))
end

-- vanilla KO has almost no Korean print media text (Print_Media 0 keys, Print_Text 3 titles), so put the
-- one Korean newspaper title and a Korean paragraph into the panel to see Hangul in SdfOldBold/SdfRegular
function KoFontTest.koreanPanel()
    local win = KoFontTest.win
    local body = win.children.body.children.textNode.children.container
    body.children.title:setText(getText("Print_Text_KnoxKnews_July1_title"))
    body.children.text:setText(getText("IGUI_health_Good") .. " / " .. getText("Fluid_Unknown") .. "\n낚시하는 법: 물고기가 바늘을 물면 낚싯줄의 장력이 늘어납니다. 똠방각하 뷁")
    print("[KoreanSdfFont] korean panel: " .. getText("Print_Text_KnoxKnews_July1_title"))
end
