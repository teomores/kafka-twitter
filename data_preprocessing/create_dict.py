topics = "Culture • Classical studies • Cooking • Critical theory • Hobbies • Literature Art • Fiction" \
         " • Game • Poetry • Sports • Performing arts • Dance • Film • Music • Opera • Theatre • Visual arts" \
         " • Architecture • Crafts • Drawing • Film • Painting • Photography • Sculpture • Typography" \
         " • Geography • Health • Exercise • Health science • Nutrition • History • Classical • Medieval" \
         " • Renaissance • Mathematics • Arithmetic • Algebra • Calculus • Discrete mathematics • Geometry" \
         " • Trigonometry • Logic • Statistics • Biology • Animals • Biochemistry • Botany • Ecology • Zoology" \
         " • Physical • Astronomy • Chemistry • Earth • Physics • Biology • Psychology • Relationships" \
         " • Philosophy • Philosophical theories • Humanism • Logic • Thinking • Transhumanism • Religion" \
         " • Social sciences • Archaeology • Critical theory • Economics • Geography • History • Linguistics" \
         " • Law • Political science • Psychology • Sociology • Relationships • Society • Community" \
         " • Criminal justice • Education • Firefighting • Law • Politics • Public affairs • Business" \
         " • Economics • Finance • Management • Marketing • Aerospace • Artificial intelligence • Agriculture" \
         " • Architecture • Big Science • Biotechnology • Communication • Computer science" \
         " • Energy development • Engineering • Firefighting • Health science • Industry" \
         " • Library • Machines • Management • Manufacturing • Military • Nutrition • Permaculture • Robotics" \
         " • Space • Telecommunication • Transport • Vehicles"

topics_list = topics.split(" • ")
with open('improved_dict.txt', 'w') as f:
    for item in topics_list:
        f.write("%s\n" % item)
