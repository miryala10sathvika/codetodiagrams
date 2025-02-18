## Manual coding phase
The sample dataset is thoroughly analyzed according to the data extraction framework with iterative coding sessions.

### Codes for RQ2
- **Architectural Notation**: The architectural notation employed for the
view representation. We follow the three main categories of notations
outlined by Clements et al. [5]: informal, where views are depicted
using general-purpose editing tools and visual conventions, with the
description’s semantics expressed in natural language (boxes, boxes_and_arrows, icons_and_arrows); semiformal,
where views are expressed in a standardized notation that specifies
graphical elements and construction rules, but lacks a complete semantic
treatment of the elements’ meaning (UML); and formal, where views are
described using notations with precise, typically mathematically-based,
semantics, generally referred to as architecture description languages
(ADLs).
- **Shapes**: The shape(s) used in the view: circles, cylinders, diamonds,
ellipses, hexagons, icons, pentagons, rectangles, squares, and
triangles.
- **Colored?**: If the view is colored (yes/no).
- **Legend?**: If the view has a legend (yes/no).
- **Nested Components?**: If the view presents nested components (yes/no).
- **Explicit Ports/Interfaces?**: If the view shows explicit ports or interfaces between components (yes/no).
- **Explicit Connectors?**: If the view shows explicit connectors, i.e., lines connecting components (yes/no).
- **Connectors Direction**: If connectors are unidirectional, bidirectional, with no explicit direction, or represented through a bus.

## Codes for RQ3
- **Architecture Scope**: If the view represents a part of the system, the entire system, or the entire system plus how it interfaces with other systems.
- **Architectural Styles**: The architectural style(s) represented in the view. Architectures are classified in the following categories: client-server; event-driven; hexagonal; layered, which also includes onion and clean architectures; map-reduce; model-view-controller, which includes all  variations, e.g., model-view-viewmodel and usecase-controller ; peer-to-peer; pipes-and-filters; publish-subscribe; rest ; service-oriented, which includes microservices architectures; and smart-contract, that mostly indicates architectures from the blockchain domain.
- **Concerns**: The view topic(s) considered. There are 7 codes identified for this field: connectivity, when the view mainly addresses connections and interactions between different components or subsystems, including communication protocols and network configurations; control
flow, when it focuses on the flow of functionalities within the software system; data flow, if the view deals with the movement and transformation of data, depicting how data is processed, stored, and exchanged; deployment, if it involves the strategies and configurations for making the system available for use; performance, when it relates to the efficiency and responsiveness of the system; scheduling, if it presents details about scheduling algorithms, task prioritization, and resource
allocation strategies; and security, if it involves the protection of the system against unauthorized access, data breaches, and other security threats.
- **Behavior**: If the view represents static, dynamic properties of the architecture, or both.
- **QAs**: The quality attribute(s) considered in the view. We stopped at the first level of the quality attributes classification of the ISO/IEC 25010:2023 [14] standard.
- **Granularity**: The granularity of the system representation: high, if the view shows only generic layers, medium if it also provides subpackages, or low if it shows details like functions or attributes. If a view presents a limited number of low-level features, but primarily stops at a high
level, it is classified as having medium granularity.
- **Components Nature**: What is the nature of architecture’s components. The main categories are: API, class, client, container, data (input and output data or files), database, device (e.g., mobile, computer, sensor), function, hardware component, layer, network element, package, server, service, step (a phase of a process), subsystem (different from package because it stands at a higher level), and technology.
- **Connectors Nature**: What is the connectors’ nature, according to the following codes: API call , represents the explicit invocation of application programming interfaces (APIs); communication, focuses on the exchange of information or messages between different components; composition, represents composition or aggregation relationships in the system; control flow, represents the flow of functionalities or control between different components of the system; data flow, illustrates
the movement and transformation of data, such as data exchange, data processing, or data storage operations; dependencies, indicates relationships and dependencies between different components; function call , represents the invocation of specific functions or methods; and inheritance, indicates inheritance relationships between classes or components.
- **Technologies**: What technologies are reported in the view (if any is documented). We stopped the classification at the level of the software provider, e.g., AWS and not AWS Lambda.
- **Design Overlays**: Additional information presented in the view to extend expressive power of representation [12], classified in: code snippets, miniviews (a zoom-in on particular aspects of the architecture), parameters, snapshots, text, and URLs.
