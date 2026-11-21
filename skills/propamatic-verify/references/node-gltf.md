# Check Three.js playback in Node

Use the project's glTF validator to check the GLB container, including the header and chunk lengths. Check the export policy for external URIs and allowed metadata before loading. Load a staged GLB with the pinned Three.js package. Compatible self-contained files whose resources need no browser decoders can use `GLTFLoader` and `AnimationMixer` directly in Node.

```javascript
import { readFileSync } from "node:fs";
import { AnimationMixer } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const bytes = readFileSync(glbPath);
const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const { scene, animations } = await new GLTFLoader().parseAsync(buffer, "");
const mixer = new AnimationMixer(scene);
```

Select clips by name. Compare evaluated poses at the endpoints and interior times against the acceptance criteria. For a repeating clip, use `LoopRepeat` and compare the pose at an interior phase with the pose one period later. Reset actions and transforms between independent checks. Verify texture decoding and material or shader appearance separately in a browser or the target engine and record them as unverified if that test was unavailable.
