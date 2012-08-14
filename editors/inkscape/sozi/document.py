
import inkex
from sets import Set

def read_xml_attr(element, attr, namespace, default = None, conversion = None):
    if namespace is None:
        ns_attr = attr
    else:
        ns_attr = inkex.addNS(attr, namespace)

    if ns_attr in element.attrib:
        value = element.attrib[ns_attr]
        if conversion is None:
            return value
        else:
            return conversion(value)
    else:
        return default


def write_xml_attr(element, attr, namespace, value):
    if namespace is None:
        ns_attr = attr
    else:
        ns_attr = inkex.addNS(attr, namespace)
        
    if value is not None:
        element.attrib[ns_attr] = value
    elif ns_attr in element.attrib:
        del element.attrib[ns_attr]


def to_boolean(value):
    return value == "true"


class SoziFrame:

    def __init__(self, document, xml = None):
        self.document = document
        
        if xml is None:
            self.xml = inkex.etree.Element(inkex.addNS("frame", "sozi"))
            self.is_attached = False
            self.is_new = True
        else:
            self.xml = xml
            self.is_attached = True
            self.is_new = False
        
        if hasattr(document, "frames"):
            default_seq = len(document.frames) + 1
        else:
            default_seq = 0

        # TODO get global defaults from the document
        self.refid = read_xml_attr(self.xml, "refid", "sozi")
        self.title = read_xml_attr(self.xml, "title", "sozi", "")
        self.sequence = read_xml_attr(self.xml, "sequence", "sozi", default_seq, int)
        self.hide = read_xml_attr(self.xml, "hide", "sozi", True, to_boolean)
        self.clip = read_xml_attr(self.xml, "clip", "sozi", True, to_boolean)
        self.timeout_enable = read_xml_attr(self.xml, "timeout-enable", "sozi", False, to_boolean)
        self.timeout_ms = read_xml_attr(self.xml, "timeout-ms", "sozi", 5000, int)
        self.transition_duration_ms = read_xml_attr(self.xml, "transition-duration-ms", "sozi", 1000, int)
        self.transition_zoom_percent = read_xml_attr(self.xml, "transition-zoom-percent", "sozi", 0, int)
        self.transition_profile = read_xml_attr(self.xml, "transition-profile", "sozi", "linear")
        self.id = read_xml_attr(self.xml, "id", None, document.effect.uniqueId("frame" + unicode(self.sequence)))

        self.layers = [ SoziLayer(self, l) for l in self.xml.xpath("sozi:layer", namespaces=inkex.NSS) ]
        self.all_layers = Set(self.layers)


    def add_layer(self, layer):
        """
        Add the given layer to the current frame.
        """
        self.layers.append(frame)
        self.all_layers.add(frame)
        layer.is_attached = True


    def delete_layer(self, index):
        """
        Remove the layer at the given index from the current frame.
        """
        layer = self.layers[index]
        del self.layers[index]
        layer.is_attached = False


    def write(self):
        """
        Commit all changes in the current frame to the SVG document.
        """
        if self.is_attached:
            if self.is_new:
                # Add element to the SVG document
                self.document.xml.getroot().append(self.xml)
                
            # TODO write only values different from the global defaults
            write_xml_attr(self.xml, "refid", "sozi", self.refid) # Optional
            write_xml_attr(self.xml, "title", "sozi", self.title)
            write_xml_attr(self.xml, "sequence", "sozi", unicode(self.sequence))
            write_xml_attr(self.xml, "hide", "sozi", "true" if self.hide else "false")
            write_xml_attr(self.xml, "clip", "sozi", "true" if self.clip else "false")
            write_xml_attr(self.xml, "timeout-enable", "sozi", "true" if self.timeout_enable else "false")
            write_xml_attr(self.xml, "timeout-ms", "sozi", unicode(self.timeout_ms))
            write_xml_attr(self.xml, "transition-duration-ms", "sozi", unicode(self.transition_duration_ms))
            write_xml_attr(self.xml, "transition-zoom-percent", "sozi", unicode(self.transition_zoom_percent))
            write_xml_attr(self.xml, "transition-profile", "sozi", self.transition_profile)
            write_xml_attr(self.xml, "id", None, self.id)

            for l in self.all_layers:
                l.write()
                
        elif not self.is_new:
            # Remove element from the SVG document
            self.document.xml.getroot().remove(self.xml)


class SoziLayer:

    def __init__(self, frame, xml):
        self.frame = frame

        if xml is None:
            self.xml = inkex.etree.Element(inkex.addNS("layer", "sozi"))
            self.is_attached = False
            self.is_new = True
        else:
            self.xml = xml
            self.is_attached = True
            self.is_new = False

        # Mandatory attributes
        self.group = read_xml_attr(self.xml, "group", "sozi")
        self.refid = read_xml_attr(self.xml, "refid", "sozi")

        # Missing attributes are inherited from the enclosing frame element
        self.hide = read_xml_attr(self.xml, "hide", "sozi", frame.hide, to_boolean)
        self.clip = read_xml_attr(self.xml, "clip", "sozi", frame.clip, to_boolean)
        self.transition_zoom_percent = read_xml_attr(self.xml, "transition-zoom-percent", "sozi", frame.transition_zoom_percent, int)
        self.transition_profile = read_xml_attr(self.xml, "transition-profile", "sozi", frame.transition_profile)

        group_xml = frame.document.xml.xpath("//*[@id='" + self.group + "']")
        label_attr = inkex.addNS("label", "inkscape")
        
        if len(group_xml) > 0 and label_attr in group_xml[0].attrib:
            self.label = group_xml[0].attrib[label_attr]
        else:
            self.label = self.group


    def write(self):
        """
        Commit all changes in the current layer to the SVG document.
        """
        if self.is_attached:
            if self.is_new:
                # Add element to the SVG document
                self.frame.xml.getroot().append(self.xml)

            # TODO write only the values that are different from the enclosing frame element
            write_xml_attr(self.xml, "group", "sozi", self.group)
            write_xml_attr(self.xml, "refid", "sozi", self.refid)
            write_xml_attr(self.xml, "hide", "sozi", "true" if self.hide else "false")
            write_xml_attr(self.xml, "clip", "sozi", "true" if self.clip else "false")
            write_xml_attr(self.xml, "transition-zoom-percent", "sozi", unicode(self.transition_zoom_percent))
            write_xml_attr(self.xml, "transition-profile", "sozi", self.transition_profile)
            
        elif not self.is_new:
            # Remove element from the SVG document
            self.frame.xml.getroot().remove(self.xml)


class SoziDocument:
    
    def __init__(self, effect):
        self.effect = effect
        self.xml = effect.document

        label_attr = inkex.addNS("label", "inkscape")
        self.layer_labels = [ g.attrib[label_attr] for g in self.xml.xpath("svg:g[@inkscape:groupmode='layer']", namespaces=inkex.NSS) if label_attr in g.attrib]
                
        self.frames = [ SoziFrame(self, f) for f in self.xml.xpath("//sozi:frame", namespaces=inkex.NSS) ]
        self.frames = sorted(self.frames, key=lambda f: f.sequence if f.sequence > 0 else len(self.frames))

        self.all_frames = Set(self.frames)
        self.renumber_from_index(0)


    def add_frame(self, frame):
        """
        Add the given frame to the document.
        """
        self.frames.append(frame)
        self.all_frames.add(frame)
        frame.is_attached = True

    
    def insert_frame(self, index, frame):
        """
        Insert the given frame at the given index.
        """
        self.frames.insert(index, frame)
        self.all_frames.add(frame)
        frame.is_attached = True
        self.renumber_from_index(index)


    def swap_frames(self, first, second):
        """
        Swap frames with the given indices.
        """
        # Swap frames in SVG document
        self.frames[first].sequence = second + 1
        self.frames[second].sequence = first + 1

        # Swap frames in model
        self.frames[first], self.frames[second] = self.frames[second], self.frames[first]


    def delete_frame(self, index):
        """
        Remove the frame at the given index from the document.
        """
        frame = self.frames[index]
        del self.frames[index]
        frame.is_attached = False
        self.renumber_from_index(index)


    def renumber_from_index(self, index):
        """
        Renumber the frames starting from the one at the given index.
        Frames will receive the following numbers: index+1, index+2, etc.
        """
        if index >= 0:
            for i in range(index, len(self.frames)):
                self.frames[i].sequence = i + 1


    def write(self):
        """
        Commit all changes in the document model to the SVG document.
        """
        for f in self.all_frames:
            f.write()

