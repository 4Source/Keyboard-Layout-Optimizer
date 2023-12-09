# ### SETUP ###
# ~~~ libraries ~~~
using Plots
using Random
using Base.Threads
using BenchmarkTools
using Statistics
using JSON


# ~~~ data ~~~
layoutPath = "layout/qwertz.layout.json"
mapPath = "map/scancode.map.json"

# ~~~ keyboard ~~~
# load Layout from 'layoutPath' (x, y, width, height, row, finger, home)
io = open(layoutPath, "r")
currentLayout = JSON.parse(io, dicttype=Dict, inttype=Float64)
close(io)
currentLayout = Dict(parse(Int,string(k))=>v  for (k,v) in pairs(currentLayout))

# load KeyMap from 'mapPath'
io = open(mapPath, "r")
currentKeyMap = JSON.parse(io, dicttype=Dict, inttype=Int64)
close(io)

handList = [1, 1, 1, 1, 2, 2, 2, 2] # what finger is with which hand

function drawKeyboard(path, id)
    plot()
    namedColours = ["yellow", "green", "blue", "red", "purple", "blue", "green", "yellow", "orange"]
    keyOffset = 0

    for i in 1:length(currentLayout)
        # print("i ")
        # print(i)
        
        keyIndex = i + keyOffset
       
        while !haskey(currentLayout, keyIndex)
            keyIndex = keyIndex + 1
            keyOffset = keyOffset + 1
        end

        # print(" keyIndex ")
        # print(keyIndex)

        layout = get(currentLayout, keyIndex, "")

        if layout != ""
            x = get(layout, "x", 0.0)
            y = get(layout, "y", 0.0)
            width = get(layout, "width", 0.0)
            height = get(layout, "height", 0.0)
            row = (Int64(get(layout, "row", 0)))
            finger = (Int64(get(layout, "finger", 0)))
            home = get(layout, "home", false)

            # print(" x ")
            # print(x)
            # print(" y ")
            # print(y)
            # print(" w ")
            # print(width)
            # print(" h ")
            # print(height)
            # print(" r ")
            # print(row)
            # print(" f ")
            # print(finger)
            # print(" h ")
            # print(home)

            myColour = namedColours[Int(finger)]

            if home 
                plot!([x], [y], shape=:rect, fillalpha = 0.2, linecolor = nothing, color = myColour, label = "", markersize = 16.5, dpi = 100)
            end
            
            plot!([x - width/2, x + width/2, x + width/2, x - width/2, x - width/2], [y - height/2, y - height/2, y + height/2, y + height/2, y - height/2], color = myColour, fillalpha = 0.2, label = "", dpi = 100)


            j = 1
            keycode = get(currentKeyMap[j], "keycode", "")
            location = get(currentKeyMap[j], "location", [0,0])

            while j <= length(currentKeyMap) && location[1] != keyIndex
                # print(keycode)
                # print(" ")
                keycode = get(currentKeyMap[j], "keycode", "")
                location = get(currentKeyMap[j], "location", [0,0])
                j = j + 1
            end
            if location[1] != keyIndex
                keycode = ""
                location = [0,0]
            end

            ""
            
            if location != [0,0] && keycode != ""
                # print(" keycode ")
                # print(keycode)
                # print(" location ")
                # print(location)
                annotate!(x, y, text(keycode, :black, :center, 10))
            end
        end
        # println()
    end

    plot!(aspect_ratio = 1, legend = false)
    
    # Check path exist or create it
    if !ispath("image/$path")
        mkdir("image/$path")
    end
    savefig("image/$path/$id.png")
end

# ### RUN ###
println("Generating...")
drawKeyboard("", "scancode")
println("Finish!")

