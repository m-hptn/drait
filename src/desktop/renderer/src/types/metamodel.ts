/**
 * TypeScript types matching the DRAIT Python metamodel
 *
 * These types correspond to the Python metamodel classes
 * and enable type-safe handling of parsed diagrams.
 */

export interface Project {
  id: string;
  name: string;
  packages: Package[];
  docstring?: string;
}

export interface Package {
  id: string;
  name: string;
  classes: Class[];
  relationships: Relationship[];
  imports?: Import[];
  docstring?: string;
}

export interface Class {
  id: string;
  name: string;
  attributes: Attribute[];
  methods: Method[];
  base_classes: string[];
  decorators: Decorator[];
  is_abstract: boolean;
  docstring?: string;
  position?: Position;
}

export interface Attribute {
  name: string;
  type: TypeReference;
  visibility: Visibility;
  is_static: boolean;
  is_class_var: boolean;
  default_value?: string;
  decorators: Decorator[];
  docstring?: string;
}

export interface Method {
  name: string;
  parameters: Parameter[];
  return_type?: TypeReference;
  visibility: Visibility;
  is_static: boolean;
  is_class_method: boolean;
  is_abstract: boolean;
  decorators: Decorator[];
  docstring?: string;
  body?: string;
}

export interface Parameter {
  name: string;
  type: TypeReference;
  kind: ParameterKind;
  default_value?: string;
}

export interface TypeReference {
  name: string;
  module?: string;
  type_arguments: TypeReference[];
  is_optional: boolean;
}

export interface Decorator {
  name: string;
  module?: string;
  arguments: Record<string, string>;
}

export interface Relationship {
  id: string;
  type: RelationshipType;
  source_id: string;
  target_id: string;
  source_role?: string;
  target_role?: string;
  source_multiplicity?: Multiplicity;
  target_multiplicity?: Multiplicity;
  is_navigable_from_source: boolean;
  is_navigable_from_target: boolean;
}

export interface Import {
  module: string;
  names: string[];
  alias?: string;
}

export interface Position {
  x: number;
  y: number;
}

// Enums

export enum Visibility {
  PUBLIC = 'public',
  PROTECTED = 'protected',
  PRIVATE = 'private',
  PACKAGE = 'package'
}

export enum RelationshipType {
  INHERITANCE = 'inheritance',
  ASSOCIATION = 'association',
  AGGREGATION = 'aggregation',
  COMPOSITION = 'composition',
  DEPENDENCY = 'dependency',
  REALIZATION = 'realization'
}

export enum ParameterKind {
  POSITIONAL = 'positional',
  KEYWORD = 'keyword',
  VAR_POSITIONAL = 'var_positional',
  VAR_KEYWORD = 'var_keyword'
}

export enum Multiplicity {
  ZERO_TO_ONE = '0..1',
  ONE = '1',
  ZERO_TO_MANY = '0..*',
  ONE_TO_MANY = '1..*'
}

// Utility functions

export function formatType(typeRef: TypeReference): string {
  let result = typeRef.name;

  if (typeRef.type_arguments && typeRef.type_arguments.length > 0) {
    const args = typeRef.type_arguments.map(formatType).join(', ');
    result += `[${args}]`;
  }

  if (typeRef.is_optional) {
    result = `Optional[${result}]`;
  }

  return result;
}

export function getVisibilitySymbol(visibility: Visibility): string {
  switch (visibility) {
    case Visibility.PUBLIC:
      return '+';
    case Visibility.PROTECTED:
      return '#';
    case Visibility.PRIVATE:
      return '-';
    case Visibility.PACKAGE:
      return '~';
    default:
      return '';
  }
}

export function getRelationshipArrow(type: RelationshipType): string {
  switch (type) {
    case RelationshipType.INHERITANCE:
      return '◁──';
    case RelationshipType.REALIZATION:
      return '◁··';
    case RelationshipType.ASSOCIATION:
      return '──>';
    case RelationshipType.AGGREGATION:
      return '◇──';
    case RelationshipType.COMPOSITION:
      return '◆──';
    case RelationshipType.DEPENDENCY:
      return '··>';
    default:
      return '──>';
  }
}
