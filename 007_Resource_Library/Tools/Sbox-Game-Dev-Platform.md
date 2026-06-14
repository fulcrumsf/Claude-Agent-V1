---
title: "Sbox Game Dev Platform"
type: tool-doc
category: app-dev
tags:
  - game-dev
  - source2
  - sandbox
created: 2026-05-08
source: local
---

## s&box

Stub

This article or section is a [stub](https://developer.valvesoftware.com/wiki/Help:Stubs "Help:Stubs"). You can help by expanding it.

s&box

[![Software Cover - S&box.jpg](https://developer.valvesoftware.com/w/images/thumb/c/c8/Software_Cover_-_S%26box.jpg/300px-Software_Cover_-_S%26box.jpg)](https://developer.valvesoftware.com/wiki/File:Software_Cover_-_S%26box.jpg)

**Developer(s)**

[Facepunch Studios](https://developer.valvesoftware.com/wiki/Facepunch_Studios "Facepunch Studios")

**Publisher(s)**

Facepunch Studios

**Release date(s)**

April 28, 2026

**Genre(s)**

[Sandbox](http://en.wikipedia.org/wiki/Sandbox_game "wp:Sandbox game")

**Platform(s)**

[Windows](https://en.wikipedia.org/wiki/Microsoft_Windows)

**Engine**

s&box (heavily modified [Half-Life: Alyx](https://developer.valvesoftware.com/wiki/Half-Life:_Alyx "Half-Life: Alyx") branch)

**Steam AppID**

[590830](https://steamdb.info/app/590830)

**Written in**

[C++](http://en.wikipedia.org/wiki/C%2B%2B "wp:C++"), [C#](http://en.wikipedia.org/wiki/C_Sharp_\(programming_language\) "wp:C Sharp (programming language)")

**Mod support**

Yes

**SDK**

s&box Game Editor (heavily modified [Half-Life: Alyx Workshop Tools](https://developer.valvesoftware.com/wiki/Half-Life:_Alyx_Workshop_Tools "Half-Life: Alyx Workshop Tools") (Developer Version))

**System requirements**

- OS: [Win 10](http://en.wikipedia.org/wiki/Windows_10 "wikipedia:Windows 10") or later
- [CPU](http://en.wikipedia.org/wiki/Central_processing_unit "wikipedia:Central processing unit"): Core i5-7500 / Ryzen 5 1600
- RAM: 8 [GB](http://en.wikipedia.org/wiki/Gigabyte "wikipedia:Gigabyte")
- Storage: 3 GB or higher disk space
- GPU: GTX 1050 / RX 570, 4GB [VRAM](http://en.wikipedia.org/wiki/Video_random-access_memory "wikipedia:Video random-access memory"), Vulkan 1.2.
- Note: Installing more addons will increase storage size.

**Distribution**

[Steam](https://developer.valvesoftware.com/wiki/Steam "Steam")

**Official website**

[Official Website](https://sbox.game/)

**Previous game**

[Garry's Mod](https://developer.valvesoftware.com/wiki/Garry%27s_Mod "Garry's Mod")

s&box is a platform and game development toolkit developed by [Facepunch](https://facepunch.com/) studio powered by a highly modified version of [Source 2](https://developer.valvesoftware.com/wiki/Source_2 "Source 2"). s&box is a spiritual successor to [Garry's Mod](https://developer.valvesoftware.com/wiki/Garry%27s_Mod "Garry's Mod"). Initially, the development was based on [Unreal Engine 4](http://en.wikipedia.org/wiki/Unreal_Engine "wikipedia:Unreal Engine"), but as soon as [Half-Life: Alyx](https://developer.valvesoftware.com/wiki/Half-Life:_Alyx "Half-Life: Alyx") came out, Facepunch immediately requested the engine branch of the newly-published game. A few weeks later [Valve](https://developer.valvesoftware.com/wiki/Valve "Valve") gave Facepunch access to the terabyte large repository, after which, in 2020, s&box's transition to Source 2 was announced. This is the first (and currently only) time that Source 2 has been licensed to third-party developers. s&box comes with a complete development package including a modified and fully featured Source 2-derived engine toolkit with C# bindings, and a distribution platform named [sbox.game](https://sbox.game/)

s&box shares similarity to game platforms like [Roblox](http://en.wikipedia.org/wiki/Roblox "wp:Roblox"). Users can create and publish their games to s&box or even directly to Steam, completely royalty-free.[^1] [^2] s&box was released on April 28, 2026. s&box's public source code can be found [here](https://github.com/Facepunch/sbox-public).

## Features

### Added

s&box runs on highly modified version of [Source 2](https://developer.valvesoftware.com/wiki/Source_2 "Source 2") with the following features:

C# scripting

Todo: Description

[Box3D physics](https://sbox.game/news/july-2025#box3d)

A new physics engine that can be quickly updated, closely related to [Rubikon](https://developer.valvesoftware.com/wiki/Rubikon "Rubikon"), and will eventually be free and open source. During development of s&box, Rubikon was switched to [Izabu](https://developer.valvesoftware.com/wiki/Izabu "Izabu"), which is a cleaned-up and modified version of Rubikon without Valve-specific code, then later being replaced again by Box3D.

Hotloading

The ability to see code changes take effect immediately with blazing fast hotloading, no need to compile and restart your game.

Mounting assets from games on different engines

In S&Box, you can mount any assets from games built on different engines. Currently as of [August 2025 Update](https://store.steampowered.com/news/app/590830/view/541112753868243026) and at launch in April 2026, S&Box can mount [Quake](https://developer.valvesoftware.com/wiki/Quake "Quake"), [GoldSrc](https://developer.valvesoftware.com/wiki/GoldSrc "GoldSrc"), [Natural Selection 2](http://www.naturalselection2.com/), and others and can spawn models or props from these games & engines.

Scenes System

s&box does away with the legacy Entity System (from [Quake engine](https://developer.valvesoftware.com/wiki/Quake_engine "Quake engine")) and utilizes a [Scene System](https://docs.facepunch.com/s/sbox-dev/doc/the-scene-system-9V88B33VlE) which lets you have a [Scene](https://docs.facepunch.com/s/sbox-dev/doc/scenes-LT2kjsMBy4) that is a collection of [Game Objects](https://docs.facepunch.com/s/sbox-dev/doc/gameobject-oUVQQzT4IO) to make up the game world. It closely resembling the way things are done in [Unity](http://en.wikipedia.org/wiki/Unity_\(game_engine\) "wikipedia:Unity (game engine)") engine.

Visual Scripting

With ActionGraph and Doo you can create interactive experiences in your levels, without having to write a single line of code, or having sprawling chains of entities. Not meant to program a game entirely in it, but to augment it.

### Changed / removed

Features that were changed or removed in s&box version of Source 2.

Removed [DirectX 11®](http://en.wikipedia.org/wiki/DirectX_11 "wikipedia:DirectX 11") ([Direct3D 11](https://developer.valvesoftware.com/wiki/Direct3D#Source_2_Direct3D "Direct3D")) support

Support for Direct3D 11 has been removed. [Vulkan](https://developer.valvesoftware.com/wiki/Vulkan "Vulkan") (1.2 or later) is required to run the game.

## UGC Content Distribution

Instead of using the [Steam Workshop](https://developer.valvesoftware.com/wiki/Steam_Workshop) for storing UGC Content s&box uses a custom web based backend called [Workshop](https://sbox.game/ugc).

## Maps

[![](https://developer.valvesoftware.com/w/images/thumb/c/cc/Sboxhammernovember2024.png/300px-Sboxhammernovember2024.png)](https://developer.valvesoftware.com/wiki/File:Sboxhammernovember2024.png)

Mappers are provided with a modified version of the Source 2 Hammer map editor, with some parts exposed for C# scripting for increased flexibility. This includes integration with the scene system which lets you place game objects with components within the map just like you would in the scene editor.

#### Project control panel

In the projects menu in the dev tools, you can restrict map selection for your game mode. You can limit it to specific curated maps or maps tagged with supporting the game mode.

#### Publication

Currently, maps can be included with a game mode or released as a separate project(one for each map). The map is published by clicking on a special button in the projects menu in the developer toolkit.

#### Characteristics

| **Available territory** | Unlimited for models, but 32768 units (624.23 m / 2048 ft) for meshes |
| --- | --- |
| **Visibility** | Unlimited. The player currently sees approximately 78740 units (2 km / 6561,68 ft) in front of him by default, but values can be increased using C# |

**Note:** Hammer will be removed in the future. Unknown when exactly but its likely to be removed when scene mesh editing is good enough to replace it.

**Warning:**Lighting baking beyond 32768 units is temporarily unavailable.

**Warning:**The nav mesh has not yet been adapted for large spaces, which will cause your OS to freeze or ran out of memory if the size of the available territory exceeds 32768 units. In the event of a freeze, the only way out will be an emergency shutdown of the computer. Turn off the navigation mesh in the map compilation window!

**Warning:**There are problems with Floating point precision. Polygons start behaving incorrectly if you are too far from the zero coordinates (faint defects start after crossing 8 km, and are extremely noticeable after 20 km)

## Programming

[![](https://developer.valvesoftware.com/w/images/thumb/9/97/S%26box-actiongraph-screenshot1.png/300px-S%26box-actiongraph-screenshot1.png)](https://developer.valvesoftware.com/wiki/File:S%26box-actiongraph-screenshot1.png)

s&box user content is programmed with C#, Microsoft's managed, object-oriented programming language of [.NET](https://en.wikipedia.org/wiki/.NET) fame. s&box includes an API which provides bindings to the underlying Source 2 engine and to Facepunch's middleware. All code in user content is distributed in source form, which s&box later compiles on-demand with [Roslyn](https://en.wikipedia.org/wiki/Roslyn_\(compiler\)). Language support is stated to permit C# 14, indicating that S&box requires a.NET 10 runtime in order to function, which is bundled with the s&box installation. Only a specific subset of the baseline.NET Core complement is available for use.

Security is a primary concern with user content. C# and its ubiquitous pairing with.NET is a software ecosystem many magnitudes larger, more complex, and more powerful than s&box or Source 2. Awarding unchecked access to this leviathan would effectively turn user content into fully-fledged applications with potentially unlimited access to the host computer. To this end, **s&box restricts the use of certain types and namespaces.** For example, access to the local file system is only available through a [sanctioned abstraction layer](https://wiki.facepunch.com/sbox/FileSystem); `System.IO.File` and similar types may **not** be used. This practice is common among applications which attempt to distill down.NET into a limited "scripting" platform for untrusted user code.

Currently, the C# API and tools are in a preview stage of development. Breaking changes happen often and the API is not yet complete.

Todo:

- Confirm exact subset of available.NET Core components.

There are many similarities between the use of C# in s&box and the use of the more primitive [Lua](https://www.lua.org/manual/5.1/) language in [Garry's Mod](https://developer.valvesoftware.com/wiki/Garry%27s_Mod "Garry's Mod"). Many concepts of GMod's Lua environment have been carried over, including limited access to the language's features and "hot reloading" of edited code.

s&box will also have a visual scripting solution called [ActionGraph](https://sbox.facepunch.com/news/action-graph/), which enables a developer to script events via nodes.

## Shaders

[![](https://developer.valvesoftware.com/w/images/thumb/d/d4/Shadergraph_Screenshot_1.png/230px-Shadergraph_Screenshot_1.png)](https://developer.valvesoftware.com/wiki/File:Shadergraph_Screenshot_1.png)

You can create your own shaders either through HLSL or through the provided Shadergraph Editor and customize their interface for the material editor.

s&box supports HLSL 2021 & Shader Model 3.0 up to 5.0.

Todo: Add more detailed information for the shader graph editor.

## Standalone games powered by s&box

*

Main article: [S&box/Standalone games](https://developer.valvesoftware.com/wiki/S%26box/Standalone_games "S&box/Standalone games")

*

## References

Expand

## External links

For Developers

- [Report a bug](https://github.com/Facepunch/sbox-public/issues)
- [Documentation](https://sbox.game/dev/doc)
- [API Reference](https://sbox.game/api)
- [Wiki](https://wiki.facepunch.com/sbox/) <sup>[<i><a href="http://en.wikipedia.org/wiki/Link_rot" title="w:Link rot">dead link</a></i>]</sup> <sup>[<i>confirm</i>]</sup>
- [Source code](https://github.com/Facepunch/sbox-public) (minus C++ code)

Other

- [News](https://sbox.facepunch.com/news)
- [Forum](https://forum.facepunch.com/)
- [Discord](http://discord.gg/sbox)

[^1]: | [1.](#cite1) | McGlynn, Anthony (30 March, 2026), [Garry's Mod creator partners with Valve in deal that ensures games made in his sandbox gem's new successor can be sold royalty-free on Steam: "It's just waiting for us now"](https://www.gamesradar.com/games/simulation/garrys-mod-creator-partners-with-valve-in-deal-that-ensures-games-made-in-his-sandbox-gems-new-successor-can-be-sold-royalty-free-on-steam-its-just-waiting-for-us-now/). *Gamesradar*. [Archived](https://web.archive.org/web/20260330162005/https://www.gamesradar.com/games/simulation/garrys-mod-creator-partners-with-valve-in-deal-that-ensures-games-made-in-his-sandbox-gems-new-successor-can-be-sold-royalty-free-on-steam-its-just-waiting-for-us-now/) from the original on 30 March, 2026. Retrieved on 17 April, 2026. |
| --- | --- |

[^2]: | [2.](#cite2) | Garry Newman (@garry) (25 March, 2026), [s&box Discord - #development channel](https://discord.com/channels/833983068468936704/833983416390385685/1486294171823112263). *[s&box Official Community Server - Discord](https://discord.gg/sbox)*. Retrieved on 17 April, 2026. "signed the standalone license with Valve btw, it's just waiting for us now" |
| --- | --- |